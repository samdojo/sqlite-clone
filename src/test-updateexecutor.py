from literalparser import LiteralParser
from sqltokenizer import Tokenizer
from data import Database, Column as OutColumn, Table, Schema
from updateexecutor import UpdateExecutor

from updateparser import UpdateParser


class TestLiteralParser:
    def setup_method(self):
        self.db = Database()
        self.db["test_schema"] = Schema()
        schema = self.db["test_schema"]
        schema["test_table1"] = Table.from_dict(
            {
                "col1": OutColumn(type=int, default=None),
                "col2": OutColumn(type=int, default=10),
                "col3": OutColumn(type=int, default=-1),
            }
        )
        self.exec = UpdateExecutor()
        self.tokenizer = Tokenizer()
        self.str_to_lit = lambda x: LiteralParser(self.tokenizer.tokenize(x)).parse()

    def test_simple1(self):
        """Test case for UPDATE statement.

        Should update only 2/3 rows.
        """
        tbl = self.db["test_schema"]["test_table1"]
        tbl.add_row({})
        tbl.add_row({})
        tbl.add_row({"col1": self.str_to_lit("2")})
        initial_rows = tbl.get_rows()
        update = UpdateParser(
            self.tokenizer.tokenize(
                """UPDATE test_schema.test_table1
        SET col1 = 2
        WHERE col1 IS NULL"""
            )
        ).parse()
        self.exec.execute(self.db, update)
        final_rows = tbl.get_rows()
        assert len([x for x in initial_rows if x["col1"] is None]) == 2
        assert len([x for x in final_rows if x["col1"] is None]) == 0
        assert len([x for x in initial_rows if x["col1"] == 2]) == 1
        assert len([x for x in final_rows if x["col1"] == 2]) == 3

    def test_simple2(self):
        """Test case for UPDATE statement.

        Uses list of cols and assignemnts.
        Skips WHERE statement (should update all cols)."""
        literal_1 = self.str_to_lit("1")
        tbl = self.db["test_schema"]["test_table1"]
        tbl.add_row({"col1": literal_1, "col2": literal_1, "col3": literal_1})
        tbl.add_row({"col1": literal_1, "col2": literal_1, "col3": literal_1})
        tbl.add_row({"col1": literal_1, "col2": literal_1, "col3": literal_1})
        tbl.add_row({"col1": literal_1, "col2": literal_1, "col3": literal_1})
        initial_rows = tbl.get_rows()
        update = UpdateParser(
            self.tokenizer.tokenize(
                """UPDATE test_schema.test_table1
        SET (col2, col3) = (4, 4)"""
            )
        ).parse()
        self.exec.execute(self.db, update)
        final_rows = tbl.get_rows()
        assert ( len( [ x for x in initial_rows if (x["col1"] == 1) and (x["col2"] == 4) and (x["col3"] == 4) ]) == 0)
        assert ( len( [ x for x in final_rows if (x["col1"] == 1) and (x["col2"] == 4) and (x["col3"] == 4) ]) == 4)

    def test_simple3(self):
        """Test case for UPDATE statement

        Uses list of cols and assignemnts and column value expressions.
        Selects all rows from simple literal expression."""
        literal_1 = self.str_to_lit("1")
        literal_2 = self.str_to_lit("2")
        literal_3 = self.str_to_lit("-1")
        tbl = self.db["test_schema"]["test_table1"]
        tbl.add_row({"col1": literal_1, "col2": literal_2, "col3": literal_3})
        tbl.add_row({"col1": literal_1, "col2": literal_2, "col3": literal_3})
        tbl.add_row({"col1": literal_1, "col2": literal_2, "col3": literal_3})
        tbl.add_row({"col1": literal_1, "col2": literal_2, "col3": literal_3})
        initial_rows = tbl.get_rows()
        update = UpdateParser(
            self.tokenizer.tokenize(
                """UPDATE test_schema.test_table1
        SET (col1, col2) = (col2, col1), col3 = col1 + col2
        WHERE 1"""
            )
        ).parse()
        self.exec.execute(self.db, update)
        final_rows = tbl.get_rows()
        assert (len([x for x in initial_rows if (x["col1"] == 2) and (x["col2"] == 1) and (x["col3"] == 3)]) == 0)
        assert (len( [ x for x in final_rows if (x["col1"] == 2) and (x["col2"] == 1) and (x["col3"] == 3) ]) == 4)

    def test_simple4(self):
        """Test case for UPDATE statement

        Replaces row 2 and 4 cols 1 and 2 with 0 value, other rows remain unchanged
        """
        literal_0 = self.str_to_lit("0")
        literal_1 = self.str_to_lit("1")
        literal_2 = self.str_to_lit("2")
        literal_m2 = self.str_to_lit("-2")
        literal_m3 = self.str_to_lit("-3")
        tbl = self.db["test_schema"]["test_table1"]
        tbl.add_row({"col1": literal_2, "col2": literal_m2, "col3": literal_2})
        tbl.add_row({"col1": literal_2, "col2": literal_m3, "col3": literal_2})
        tbl.add_row({"col1": literal_1, "col2": literal_1, "col3": literal_2})
        tbl.add_row({"col1": literal_1, "col2": literal_m2, "col3": literal_2})
        update = UpdateParser(
            self.tokenizer.tokenize(
                """UPDATE test_schema.test_table1
        SET col1 = 0, col2 = 0
        WHERE (col1 + col2) < 0"""
            )
        ).parse()
        self.exec.execute(self.db, update)
        final_rows = tbl.get_rows()
        expected_rows = [
            tbl.create_entry(
                {"col1": literal_2, "col2": literal_m2, "col3": literal_2}
            ),
            tbl.create_entry({"col1": literal_0, "col2": literal_0, "col3": literal_2}),
            tbl.create_entry({"col1": literal_1, "col2": literal_1, "col3": literal_2}),
            tbl.create_entry({"col1": literal_0, "col2": literal_0, "col3": literal_2}),
        ]
        final_rows.sort(key=lambda x: (x["col1"], x["col2"], x["col3"]))
        expected_rows.sort(key=lambda x: (x["col1"], x["col2"], x["col3"]))
        assert final_rows == expected_rows
