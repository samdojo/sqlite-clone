from baseexecuter import ExecutingException

from data import Database
from statements import InsertStatement, Literal


class InsertTableExecutor:
    def execute(self, db: Database, input: InsertStatement):
        schema = db[input.schema_name]
        if input.table_name not in schema.keys():
            if input.schema_name is None:
                raise ExecutingException(
                    f"Insert table {input.table_name} not found in default schema"
                )

            raise ExecutingException(
                f"Insert table {input.table_name} not found in schema {input.schema_name}"
            )
        table = schema[input.table_name]
        insert_columns: list[str] = (
            input.column_names if input.column_names else table.ordered_columns
        )
        if len(set(insert_columns) - set(table.ordered_columns)) > 0:
            raise ExecutingException(
                f"INSERT statement references column(s) `{list(set(insert_columns) - set(table.ordered_columns))}` which do not exist in table {input.table_name}"
            )
        insert_map: dict[str, Literal] = {}
        if len(insert_columns) != len(input.values):
            raise ExecutingException(
                f"INSERT statement expected exactly {len(insert_columns)} values to insert into table, received {len(input.values)} values"
            )
        for idx, expr in enumerate(input.values):
            expr = expr.apply_unary_operator()[1]
            if expr.route != 1 or not isinstance(expr.lead_expr, Literal):
                raise ExecutingException(
                    f"Found non-literal data {expr} in VALUE list of INSERT statement."
                )
            insert_map[insert_columns[idx]] = expr.lead_expr
        table.add_entry(insert_map)
