# test_columnparser.py
import unittest
from columnparser import ColumnParser
from statements import Column
from sqltoken import Token, TokenType


def make_tokens(*args):
    """
    Convert strings to Token objects.
    Keywords are KEYWORD, everything else is IDENTIFIER.
    """
    keywords = {"PRIMARY", "KEY", "NOT", "NULL", "UNIQUE", "DEFAULT"}
    tokens = []
    for arg in args:
        tok_type = TokenType.KEYWORD if arg.upper() in keywords else TokenType.IDENTIFIER
        tokens.append(Token(tok_type, arg))
    return tokens


class TestColumnParser(unittest.TestCase):
    def test_simple_column(self):
        tokens = make_tokens("id", "INTEGER")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "id")
        self.assertEqual(col.type, "INTEGER")
        self.assertTrue(col.nullable)
        self.assertFalse(col.primary_key)
        self.assertFalse(col.unique)
        self.assertIsNone(col.default)

    def test_not_null_column(self):
        tokens = make_tokens("name", "TEXT", "NOT", "NULL")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "name")
        self.assertEqual(col.type, "TEXT")
        self.assertFalse(col.nullable)

    def test_primary_key_column(self):
        tokens = make_tokens("id", "INTEGER", "PRIMARY", "KEY")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "id")
        self.assertEqual(col.type, "INTEGER")
        self.assertFalse(col.nullable)
        self.assertTrue(col.primary_key)

    def test_unique_column(self):
        tokens = make_tokens("email", "TEXT", "UNIQUE")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertTrue(col.unique)

    def test_default_column(self):
        tokens = make_tokens("age", "INTEGER", "DEFAULT", "18")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.default, "18")

    def test_multiple_constraints(self):
        tokens = make_tokens("username", "TEXT", "NOT", "NULL", "UNIQUE", "DEFAULT", "'guest'")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "username")
        self.assertEqual(col.type, "TEXT")
        self.assertFalse(col.nullable)
        self.assertTrue(col.unique)
        self.assertEqual(col.default, "'guest'")


if __name__ == "__main__":
    unittest.main()
