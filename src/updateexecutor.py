import math
from typing import TypeAlias

from data import Database, Entry
from statements import Expression, UpdateStatement


def float_is_zero(f: float) -> bool:
    return math.isclose(f, 0.0)


#
SetAssignments: TypeAlias = list[dict[str, list[str] | Expression | bool]]


class UpdateExecutor:
    def execute(self, db: Database, input: UpdateStatement) -> None:
        table = db[input.table.schema_name][input.table.table_name]
        assignments = self.simplify_set_assignments(input.set_assignments)
        where: Expression = input.where_expr
        rows = table.get_rows()

        # Step 1: filter rows based on where condition
        target_rows = [row for row in rows if (where.evaluate(row) if where else True)]

        # Step 2: Create new record from old record + assignments
        old_new_rows = [
            self.evaluate_set_assignments(row, assignments) for row in target_rows
        ]

        # Step 3: Call update record on table
        for old, new in old_new_rows:
            table.update_entry(old, new)

    @staticmethod
    def simplify_set_assignments(assigns: SetAssignments) -> dict[str, Expression]:
        output = {}
        for a in assigns:
            if not a["is_column_list"]:
                output[a["columns"][0]] = a["expression"]
                continue
            a_top_expr: Expression = a["expression"]
            if a_top_expr.route != 8:
                raise ValueError(
                    "Update statement set expression was supposed to be a list of expressions."
                )
            for col_name, expr in zip(a["columns"], a_top_expr.expr_array):
                output[col_name] = expr
        return output

    @staticmethod
    def evaluate_set_assignments(
        row: Entry, assigns: dict[str, Expression]
    ) -> tuple[Entry, Entry]:
        new_assignments = {field: expr.evaluate(row) for field, expr in assigns.items()}
        return (row, row._replace(**new_assignments))
