import unittest
from columnparser import ColumnParser
from statements import Column
from sqltokenizer import Tokenizer  


def tokenize(sql_fragment: str):
    """
    Helper to run Tokenizer on a fake column definition fragment.
    """
    tokenizer = Tokenizer()
    return tokenizer.tokenize(sql_fragment) 


class TestColumnParser(unittest.TestCase):
    def test_simple_column(self):
        tokens = tokenize("id INTEGER")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "id")
        self.assertEqual(col.type, "INTEGER")
        self.assertTrue(col.nullable)
        self.assertFalse(col.primary_key)
        self.assertFalse(col.unique)
        self.assertIsNone(col.default)

    def test_not_null_column(self):
        tokens = tokenize("name TEXT NOT NULL")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "name")
        self.assertEqual(col.type, "TEXT")
        self.assertFalse(col.nullable)

    def test_primary_key_column(self):
        tokens = tokenize("id INTEGER PRIMARY KEY")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "id")
        self.assertEqual(col.type, "INTEGER")
        self.assertFalse(col.nullable)
        self.assertTrue(col.primary_key)

    def test_unique_column(self):
        tokens = tokenize("email TEXT UNIQUE")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertTrue(col.unique)

    def test_default_column(self):
        tokens = tokenize("age INTEGER DEFAULT 18")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.default, "18")

    def test_multiple_constraints(self):
        tokens = tokenize("username TEXT NOT NULL UNIQUE DEFAULT 'guest'")
        parser = ColumnParser(tokens)
        col = parser.parse()
        self.assertEqual(col.name, "username")
        self.assertEqual(col.type, "TEXT")
        self.assertFalse(col.nullable)
        self.assertTrue(col.unique)
        self.assertEqual(col.default, "'guest'")


if __name__ == "__main__":
    unittest.main()
