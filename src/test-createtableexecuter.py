from statements import CreateTableStatement, Column as InColumn
from data import Database, Column as OutColumn
from createtableexecuter import CreateTableExecuter


class TestLiteralParser:
    def setup_method(self):
        self.db = Database()
        self.exec = CreateTableExecuter()

    def test_simple(self):
        person_table = CreateTableStatement('Person', None, [InColumn('name', str, False), InColumn('age', int, False)])
        self.exec.execute(self.db, person_table)
        assert len(self.db) == 1
        default_schema = self.db[None]
        assert isinstance(default_schema, dict)
        assert len(default_schema) == 1
        person_table = default_schema['Person']
        assert isinstance(person_table, dict)
        assert len(person_table) == 2
        col1 = person_table['name']
        assert isinstance(col1, OutColumn)
        assert col1.type == str
        col2 = person_table['age']
        assert isinstance(col2, OutColumn)
        assert col2.type == int

    def test_schema(self):
        person_table = CreateTableStatement('Person', 'Schema', [InColumn('name', str, False), InColumn('age', int, False)])
        self.exec.execute(self.db, person_table)
        assert len(self.db) == 2
        default_schema = self.db['Schema']
        assert isinstance(default_schema, dict)
        assert len(default_schema) == 1
        person_table = default_schema['Person']
        assert isinstance(person_table, dict)
        assert len(person_table) == 2
        col1 = person_table['name']
        assert isinstance(col1, OutColumn)
        assert col1.type == str
        col2 = person_table['age']
        assert isinstance(col2, OutColumn)
        assert col2.type == int
