import unittest
from typing import List
from sqltoken import Token, TokenType
from updateparser import UpdateParser
from baseparser import ParsingException
from statements import UpdateStatement
from expr import Expression


class TestUpdateParser(unittest.TestCase):

    def test_basic_update_statement(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("users", TokenType.IDENTIFIER),
            Token("SET", TokenType.KEYWORD),
            Token("name", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("'Alice'", TokenType.STRING),
            Token("WHERE", TokenType.KEYWORD),
            Token("id", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("1", TokenType.NUMBER),
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
            Token("=", TokenType.EQ),
            Token("99.99", TokenType.NUMBER),
            Token(",", TokenType.COMMA),
            Token("stock", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("100", TokenType.NUMBER),
        ]
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertEqual(len(statement.set_assignments), 2)
        self.assertEqual(statement.set_assignments[0]['columns'][0], "price")
        self.assertEqual(statement.set_assignments[0]['expression'].value, "99.99")
        self.assertEqual(statement.set_assignments[1]['columns'][0], "stock")
        self.assertEqual(statement.set_assignments[1]['expression'].value, "100")

    def test_update_with_column_list_assignment(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("users", TokenType.IDENTIFIER),
            Token("SET", TokenType.KEYWORD),
            Token("(", TokenType.LPAREN),
            Token("first_name", TokenType.IDENTIFIER),
            Token(",", TokenType.COMMA),
            Token("last_name", TokenType.IDENTIFIER),
            Token(")", TokenType.RPAREN),
            Token("=", TokenType.EQ),
            Token("(", TokenType.LPAREN),
            Token("'John'", TokenType.STRING),
            Token(",", TokenType.COMMA),
            Token("'Doe'", TokenType.STRING),
            Token(")", TokenType.RPAREN),
        ]
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertEqual(len(statement.set_assignments), 1)
        self.assertEqual(statement.set_assignments[0]['columns'], ["first_name", "last_name"])
        self.assertTrue(statement.set_assignments[0]['is_column_list'])
        self.assertEqual(len(statement.set_assignments[0]['expression'].children), 2)
        self.assertEqual(statement.set_assignments[0]['expression'].children[0].value, "'John'")
        self.assertEqual(statement.set_assignments[0]['expression'].children[1].value, "'Doe'")

    def test_update_with_or_action(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("OR", TokenType.KEYWORD),
            Token("REPLACE", TokenType.KEYWORD),
            Token("inventory", TokenType.IDENTIFIER),
            Token("SET", TokenType.KEYWORD),
            Token("quantity", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("quantity", TokenType.IDENTIFIER),
            Token("+", TokenType.PLUS),
            Token("1", TokenType.NUMBER),
        ]
        parser = UpdateParser(tokens)
        statement = parser.parse()
        
        self.assertEqual(statement.or_action, "REPLACE")
        self.assertEqual(statement.table.name, "inventory")

    def test_update_with_from_clause(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("T1", TokenType.IDENTIFIER),
            Token("SET", TokenType.KEYWORD),
            Token("col1", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("T2", TokenType.IDENTIFIER),
            Token(".", TokenType.DOT),
            Token("col2", TokenType.IDENTIFIER),
            Token("FROM", TokenType.KEYWORD),
            Token("T2", TokenType.IDENTIFIER),
            Token("WHERE", TokenType.KEYWORD),
            Token("T1", TokenType.IDENTIFIER),
            Token(".", TokenType.DOT),
            Token("id", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("T2", TokenType.IDENTIFIER),
            Token(".", TokenType.DOT),
            Token("id", TokenType.IDENTIFIER),
        ]
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertIsNotNone(statement.from_clause)
        self.assertEqual(statement.from_clause.name, "T2")

    def test_update_with_returning_clause(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("users", TokenType.IDENTIFIER),
            Token("SET", TokenType.KEYWORD),
            Token("status", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("'active'", TokenType.STRING),
            Token("RETURNING", TokenType.KEYWORD),
            Token("id", TokenType.IDENTIFIER),
            Token(",", TokenType.COMMA),
            Token("name", TokenType.IDENTIFIER),
        ]
        parser = UpdateParser(tokens)
        statement = parser.parse()

        self.assertIsNotNone(statement.returning_exprs)
        self.assertEqual(len(statement.returning_exprs), 2)
        self.assertEqual(statement.returning_exprs[0].value, "id")
        self.assertEqual(statement.returning_exprs[1].value, "name")

    def test_parsing_exception_no_update_keyword(self):
        tokens = [
            Token("SELECT", TokenType.KEYWORD),
            Token("*", TokenType.STAR),
            Token("FROM", TokenType.KEYWORD),
            Token("users", TokenType.IDENTIFIER),
        ]
        parser = UpdateParser(tokens)
        with self.assertRaises(ParsingException) as context:
            parser.parse()
        self.assertIn("Expected UPDATE", str(context.exception))

    def test_parsing_exception_no_set_keyword(self):
        tokens = [
            Token("UPDATE", TokenType.KEYWORD),
            Token("users", TokenType.IDENTIFIER),
            Token("WHERE", TokenType.KEYWORD),
            Token("id", TokenType.IDENTIFIER),
            Token("=", TokenType.EQ),
            Token("1", TokenType.NUMBER),
        ]
        parser = UpdateParser(tokens)
        with self.assertRaises(ParsingException) as context:
            parser.parse()
        self.assertIn("Expected SET in UPDATE statement", str(context.exception))

if __name__ == '__main__':
    unittest.main()