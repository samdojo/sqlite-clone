import math
from typing import Any, Optional, TypeAlias

from data import Database
from statements import Expression, QualifiedTableName

def float_is_zero(f: float) -> bool:
    return math.isclose(f, 0.0)


class UpdateStatement:
    table: QualifiedTableName  # QualifiedTableName
    set_assignments: list[dict[str, Any]]  # [{'columns': [...], 'expression': ..., 'is_column_list': bool}]
    from_clause: Optional[Any] = None  # TableOrSubQuery
    where_expr: Optional[Any] = None   # Expression returning_exprs: Optional[list[Any]] = None  # List[Expression] or_action: Optional[str] = None    # "ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"

SetAssignments: TypeAlias = list[dict[str, list[str] | Expression | bool ]]
class DummyUpdateStatement:
    table: QualifiedTableName
    set_assignments: SetAssignments
    where_expr: Expression


class UpdateExecutor:
    def execute(self, db: Database, input: DummyUpdateStatement) -> None:
        table = db[input.table.schema_name][input.table.table_name]
        assignments = self.simplify_set_assignments(input.set_assignments)
        where = input.where_expr
        rows = table.get_rows()

        # Step 1: filter rows based on where condition
        target_rows = [row for row in rows if evaluate_where(where, row)]

        # Step 2: Create new record from old record + assignments
        old_new_rows = [evaluate_assignments(assignments, row) for row in target_rows]

        # Step 3: Call update record on table
        for old, new in old_new_rows:
            table.update_entry(old, new)

    @staticmethod
    def simplify_set_assignments(assigns: SetAssignments) -> list[tuple[str, Expression]]:
        output = []
        for a in assigns:
            if not a["is_column_list"]:
                single_assignment = (a["columns"][0], a["expression"][0])
                output.append(single_assignment)
                continue
            a_top_expr: Expression = a["expression"]
            if a_top_expr.route != 8:
                raise ValueError(
                    "Update statement set expression was supposed to be a list of expressions."
                )
            output.extend(zip(a["columns"], a_top_expr.expr_array))
        return output
