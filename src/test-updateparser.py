import unittest
from sqltoken import Token, TokenType
from updateparser import UpdateParser
from baseparser import ParsingException
from statements import UpdateStatement

class TestUpdateParser(unittest.TestCase):

    def test_basic_update_statement(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("users", TokenType.IDENTIFIER),
            Token("SET", TokenType.KEYWORD),
            Token("name", TokenType.IDENTIFIER),
            Token("=", TokenType.OPERATOR),
            Token("'Alice'", TokenType.STRING_LITERAL),
            Token("WHERE", TokenType.KEYWORD),
            Token("id", TokenType.IDENTIFIER),
            Token("=", TokenType.OPERATOR),
            Token("1", TokenType.NUMBER_LITERAL),
        ]
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertIsInstance(statement, UpdateStatement)
        self.assertEqual(statement.table.name, "users")
        self.assertEqual(len(statement.set_assignments), 1)
        self.assertEqual(statement.set_assignments[0]['columns'][0], "name")
        self.assertEqual(statement.set_assignments[0]['expression'].value, "'Alice'")
        self.assertEqual(statement.where_expr.left.value, "id")
        self.assertEqual(statement.where_expr.right.value, "1")
        self.assertIsNone(statement.from_clause)
        self.assertIsNone(statement.returning_exprs)
        self.assertIsNone(statement.or_action)

    def test_update_with_multiple_set_assignments(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("products", TokenType.IDENTIFIER),
            Token("SET", TokenType.KEYWORD),
            Token("price", TokenType.IDENTIFIER),
            Token("=", TokenType.OPERATOR),
            Token("99.99", TokenType.NUMBER_LITERAL),
            Token(",", TokenType.COMMA),
            Token("stock", TokenType.IDENTIFIER),
            Token("=", TokenType.OPERATOR),
            Token("100", TokenType.NUMBER_LITERAL),
        ]
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertEqual(len(statement.set_assignments), 2)
        self.assertEqual(statement.set_assignments[0]['columns'][0], "price")
        self.assertEqual(statement.set_assignments[0]['expression'].value, "99.99")
        self.assertEqual(statement.set_assignments[1]['columns'][0], "stock")
        self.assertEqual(statement.set_assignments[1]['expression'].value, "100")


if __name__ == '__main__':
    unittest.main()
