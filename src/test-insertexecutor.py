from baseexecuter import ExecutingException
from sqltokenizer import Tokenizer
from data import Database, Column as OutColumn, Table, Schema
from insertexecutor import InsertTableExecutor
from insertparser import InsertStatementParser
import pytest


class TestLiteralParser:
    def setup_method(self):
        self.db = Database()
        self.db["test_schema"] = Schema()
        schema = self.db["test_schema"]
        schema["test_table1"] = Table(column_list=["col1", "col2", "col3"])
        schema["test_table1"]["col1"] = OutColumn(type=int, default=None)
        schema["test_table1"]["col2"] = OutColumn(type=int, default=10)
        schema["test_table1"]["col3"] = OutColumn(type=int, default=None)
        schema["test_table2"] = Table(column_list=["colA", "colB", "colC", "colD"])
        schema["test_table2"]["colA"] = OutColumn(type=str, default="")
        schema["test_table2"]["colB"] = OutColumn(type=float, default=5.5)
        schema["test_table2"]["colC"] = OutColumn(type=int, default=None)
        schema["test_table2"]["colD"] = OutColumn(type=bool, default=True)
        schema["test_table3"] = Table(column_list=["col4", "col5", ])
        schema["test_table3"]["col4"] = OutColumn(type=int, default=None)
        schema["test_table3"]["col5"] = OutColumn(type=int, default=10)
        self.exec = InsertTableExecutor()
        self.tokenizer = Tokenizer()

    def test_simple(self):
        schema = "test_schema"
        tbl = "test_table1"
        target_tbl = self.db[schema][tbl]
        tokens = self.tokenizer.tokenize(f"INSERT INTO {schema}.{tbl} VALUES (1, 2, 3)")
        insert_statement = InsertStatementParser(tokens).parse()
        self.exec.execute(self.db, insert_statement)
        col1_final = len(target_tbl["col1"].get(1))
        assert col1_final == 1

    def test_column_defaults(self):
        schema = "test_schema"
        tbl = "test_table1"
        target_tbl = self.db[schema][tbl]
        tokens_1 = self.tokenizer.tokenize(
            f"INSERT INTO {schema}.{tbl} (col1, col3) VALUES (1, 3)"
        )
        insert_1 = InsertStatementParser(tokens_1).parse()
        tokens_2 = self.tokenizer.tokenize(
            f"INSERT INTO {schema}.{tbl} (col1) VALUES (1)"
        )
        insert_2 = InsertStatementParser(tokens_2).parse()
        self.exec.execute(self.db, insert_1)
        self.exec.execute(self.db, insert_2)
        col1_final = len(target_tbl["col1"].get(1))
        assert col1_final == 2
        col2_final = len(target_tbl["col2"].get(10))
        assert col2_final == 2
        col3_final = len(target_tbl["col3"].get(3))
        assert col3_final == 1
        col3_final = len(target_tbl["col3"].get(None))
        assert col3_final == 1

    def test_multi_statements(self):
        schema = "test_schema"
        tbl = "test_table2"
        target_tbl = self.db[schema][tbl]
        tokens_1 = self.tokenizer.tokenize(
            # TODO: Need to flatten UNARY Expression and its underlying
            # expression
            # Lowkey also binary expressions but we'll deal with that later.
            f"INSERT INTO {schema}.{tbl} (colB, colC) VALUES (-1.0, NULL)"
        )
        insert_1 = InsertStatementParser(tokens_1).parse()
        tokens_2 = self.tokenizer.tokenize(
            f"INSERT INTO {schema}.{tbl} (colA, colC) VALUES ('cat', NULL)"
        )
        insert_2 = InsertStatementParser(tokens_2).parse()
        tokens_3 = self.tokenizer.tokenize(
            f"INSERT INTO {schema}.{tbl} (colA, colB) VALUES ('3.0', 3.0)"
        )
        insert_3 = InsertStatementParser(tokens_3).parse()
        self.exec.execute(self.db, insert_1)
        self.exec.execute(self.db, insert_2)
        self.exec.execute(self.db, insert_3)
        col1_final = len(target_tbl["colA"].get(None))
        assert col1_final == 0
        col1_final = len(target_tbl["colA"].get(""))
        assert col1_final == 1
        col2_final = set(target_tbl["colB"].between(0.0, 10.0))
        assert col2_final == {3.0, 5.5}
        col3_final = len(target_tbl["colC"].get(None))
        assert col3_final == 3
        col3_final = len(target_tbl["colD"].get(True))
        assert col3_final == 3

    def test_too_few_values_explicit(self):
        schema = "test_schema"
        tbl = "test_table3"
        target_tbl = self.db[schema][tbl]
        tokens = self.tokenizer.tokenize(f"INSERT INTO {schema}.{tbl} (col4, col5) VALUES (1)")
        insert_statement = InsertStatementParser(tokens).parse()
        with pytest.raises(ExecutingException) as p_err:
            self.exec.execute(self.db, insert_statement)
        assert p_err.errisinstance(ExecutingException)
        assert len(target_tbl["col4"].get(1)) == 0 

    def test_too_few_values_implicit(self):
        schema = "test_schema"
        tbl = "test_table3"
        target_tbl = self.db[schema][tbl]
        tokens = self.tokenizer.tokenize(f"INSERT INTO {schema}.{tbl} VALUES (1)")
        insert_statement = InsertStatementParser(tokens).parse()
        with pytest.raises(ExecutingException) as p_err:
            self.exec.execute(self.db, insert_statement)
        assert p_err.errisinstance(ExecutingException)
        assert len(target_tbl["col4"].get(1)) == 0 

    def test_too_many_values(self):
        schema = "test_schema"
        tbl = "test_table3"
        target_tbl = self.db[schema][tbl]
        tokens = self.tokenizer.tokenize(f"INSERT INTO {schema}.{tbl} VALUES (1, 2, 3 )")
        insert_statement = InsertStatementParser(tokens).parse()
        with pytest.raises(ExecutingException) as p_err:
            self.exec.execute(self.db, insert_statement)
        assert p_err.errisinstance(ExecutingException)
        assert len(target_tbl["col4"].get(1)) == 0 

    def test_wrong_columns(self):
        schema = "test_schema"
        tbl = "test_table3"
        tokens = self.tokenizer.tokenize(f"INSERT INTO {schema}.{tbl} (colAA, colBB) VALUES (1, 2)")
        insert_statement = InsertStatementParser(tokens).parse()
        with pytest.raises(ExecutingException) as p_err:
            self.exec.execute(self.db, insert_statement)
        assert p_err.errisinstance(ExecutingException)

    def test_wrong_datatypes(self):
        schema = "test_schema"
        tbl = "test_table3"
        target_tbl = self.db[schema][tbl]
        tokens = self.tokenizer.tokenize(f"INSERT INTO {schema}.{tbl} (col4, col5) VALUES (1.0, 'ROW_VAL')")
        insert_statement = InsertStatementParser(tokens).parse()
        with pytest.raises(ExecutingException) as p_err:
            self.exec.execute(self.db, insert_statement)
        assert p_err.errisinstance(ExecutingException)
        assert len(target_tbl["col4"].get(1)) == 0 

