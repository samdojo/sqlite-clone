from baseexecuter import ExecutingException
from sqltokenizer import Tokenizer
from data import Database, Column as OutColumn, Table, Schema
from updateexecutor import UpdateExecutor, UpdateStatement
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
        self.exec = UpdateExecutor()
        self.tokenizer = Tokenizer()

    def test_simple1(self):
        """Test case for UPDATE statement

        UPDATE test_schema.test_table1
        SET col1 = 2
        WHERE col1 IS NONE"""

    def test_simple2(self):
        """Test case for UPDATE statement

        UPDATE test_schema.test_table1
        SET col1 = 2, (col2, col3) = (4, 4)
        WHERE col1 IS NONE"""

    def test_simple3(self):
        """Test case for UPDATE statement

        UPDATE test_schema.test_table1
        SET col1 = 2, (col2, col3) = (4, 4)
        WHERE TRUE"""

    def test_simple4(self):
        """Test case for UPDATE statement

        UPDATE test_schema.test_table1
        SET col1 = col2 + col3, (col2, col3) = (col3, col2)
        WHERE col1 IS NONE"""
