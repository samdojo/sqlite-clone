from statements import CreateTableStatement
from data import Database, Table, Column, Schema
from baseexecuter import ExecutingException

class CreateTableExecuter:
    def execute(self, db: Database, input: CreateTableStatement):
        if not input.schema_name in db:
            db[input.schema_name] = Schema()
        schema = db[input.schema_name]
        if input.table_name in schema:
            raise ExecutingException('table already exists')

        schema[input.table_name] = Table()
        table = schema[input.table_name]

        for col in input.columns:
            table[col.name] = Column(col.type, col.default)
