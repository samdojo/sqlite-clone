import unittest
from selectparser import SelectParser
from statements import SelectStatement
from sqltokenizer import Tokenizer  


def tokenize(sql_fragment: str):
    """Helper to run Tokenizer on a SQL statement."""
    tokenizer = Tokenizer()
    return tokenizer.tokenize(sql_fragment) 


class TestSelectParser(unittest.TestCase):
    def test_simple_select(self):
        tokens = tokenize("SELECT id, name FROM users")
        parser = SelectParser(tokens)
        stmt = parser.parse()
        self.assertIsInstance(stmt, SelectStatement)
        self.assertEqual(stmt.columns, ["id", "name"])
        self.assertEqual(stmt.table, "users")
        self.assertIsNone(stmt.where)

    def test_select_single_column(self):
        tokens = tokenize("SELECT id FROM accounts")
        parser = SelectParser(tokens)
        stmt = parser.parse()
        self.assertIsInstance(stmt, SelectStatement)
        self.assertEqual(stmt.columns, ["id"])
        self.assertEqual(stmt.table, "accounts")
        self.assertIsNone(stmt.where)

    def test_select_with_where(self):
        tokens = tokenize("SELECT id, email FROM users WHERE active = 1")
        parser = SelectParser(tokens)
        stmt = parser.parse()
        self.assertIsInstance(stmt, SelectStatement)
        self.assertEqual(stmt.columns, ["id", "email"])
        self.assertEqual(stmt.table, "users")
        self.assertEqual(stmt.where, "active = 1")

    def test_select_with_complex_where(self):
        tokens = tokenize("SELECT * FROM logs WHERE level = 'ERROR' AND date > '2024-01-01'")
        parser = SelectParser(tokens)
        stmt = parser.parse()
        self.assertIsInstance(stmt, SelectStatement)
        self.assertEqual(stmt.columns, ["*"])
        self.assertEqual(stmt.table, "logs")
        self.assertEqual(stmt.where, "level = 'ERROR' AND date > '2024-01-01'")

    # Existing edge cases
    def test_missing_from(self):
        tokens = tokenize("SELECT id, name users")  # missing FROM keyword
        parser = SelectParser(tokens)
        with self.assertRaises(Exception):
            parser.parse()

    def test_missing_columns(self):
        tokens = tokenize("SELECT FROM users")  # missing columns
        parser = SelectParser(tokens)
        with self.assertRaises(Exception):
            parser.parse()

    # Additional edge cases suggested by Sam
    def test_empty_column_before_comma(self):
        tokens = tokenize("SELECT , FROM users")
        parser = SelectParser(tokens)
        with self.assertRaises(Exception):
            parser.parse()

    def test_empty_column_before_valid_column(self):
        tokens = tokenize("SELECT , id FROM users")
        parser = SelectParser(tokens)
        with self.assertRaises(Exception):
            parser.parse()

    def test_missing_comma_between_columns(self):
        tokens = tokenize("SELECT id name FROM users")
        parser = SelectParser(tokens)
        with self.assertRaises(Exception):
            parser.parse()


if __name__ == "__main__":
    unittest.main()
