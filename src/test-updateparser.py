import unittest
from sqltoken import Token, TokenType
from sqltokenizer import Tokenizer
from updateparser import UpdateParser
from baseparser import ParsingException
from statements import UpdateStatement


class TestUpdateParser(unittest.TestCase):

    def test_basic_update_statement(self):
        t = Tokenizer()
        tokens = t.tokenize("UPDATE users SET name = 'Alice' WHERE id = 1")
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, UpdateStatement)
        self.assertEqual(statement.table.table_name, "users")
        self.assertEqual(len(statement.set_assignments), 1)
        self.assertEqual(statement.set_assignments[0]['columns'][0], "name")
        self.assertEqual(statement.set_assignments[0]['expression'].lead_expr.value, "Alice")
        self.assertEqual(statement.where_expr.lead_expr.lead_expr.column_name, "id")
        self.assertEqual(statement.where_expr.second_expr.lead_expr.value, 1)
        self.assertIsNone(statement.from_clause)
        self.assertIsNone(statement.returning_exprs)
        self.assertIsNone(statement.or_action)

    def test_update_with_multiple_set_assignments(self):
        t = Tokenizer()
        tokens = t.tokenize("UPDATE products SET price = 99.99, stock = 100")
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertEqual(len(statement.set_assignments), 2)
        self.assertEqual(statement.set_assignments[0]['columns'][0], "price")
        self.assertEqual(statement.set_assignments[0]['expression'].lead_expr.value, 99.99)
        self.assertEqual(statement.set_assignments[1]['columns'][0], "stock")
        self.assertEqual(statement.set_assignments[1]['expression'].lead_expr.value, 100)


if __name__ == '__main__':
    unittest.main()
