from baseexecuter import ExecutingException
from data import Database
from statements import SelectStatement


class SelectExecuter:
    def execute(self, db: Database, input: SelectStatement):
        schema = db[input.schema_name]
        if input.table_name not in schema.keys():
            if input.schema_name is None:
                raise ExecutingException(
                    f"Select table {input.table_name} not found in default schema"
                )
            raise ExecutingException(
                f"Select table {input.table_name} not found in schema {input.schema_name}"
            )
        table = schema[input.table_name]

        if len(input.columns) == 0:
            selected_columns = table.ordered_columns
        else:
            invalid_columns = set(input.columns) - set(table.ordered_columns)
            if invalid_columns:
                raise ExecutingException(
                    f"Column(s) {list(invalid_columns)} do not exist in table {input.table_name}"
                )
            selected_columns = input.columns

        if len(table.ordered_columns) == 0:
            return []  # Empty table

        first_column = table[table.ordered_columns[0]]
        all_entries = []

        for key in first_column:
            all_entries.extend(first_column[key])

        all_entries.extend(first_column.none_entries)

        result = []
        for entry in all_entries:
            row = {}
            for col_name in selected_columns:
                row[col_name] = entry[col_name]
            result.append(row)

        return result
