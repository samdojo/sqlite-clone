import unittest
from lexer import Lexer, LexingException
from updateparser import UpdateParser
from statements import UpdateStatement, QualifiedTableName, Expression, TableOrSubQuery
from sqltoken import TokenType, Token
from baseparser import ParsingException

class TestUpdateParser(unittest.TestCase):
    
    def setUp(self):
        """Set up a fresh lexer for each test."""
        self.lexer = Lexer()

    def parse_statement(self, sql):
        """Helper to tokenize and parse a single SQL statement."""
        tokens = self.lexer.tokenize(sql)
        parser = UpdateParser(tokens)
        return parser.parse()

    def test_basic_update_statement(self):
        """Test a simple UPDATE statement with one assignment."""
        sql = "UPDATE users SET age = 30 WHERE id = 1;"
        statement = self.parse_statement(sql)
        
        self.assertIsInstance(statement, UpdateStatement)
        self.assertIsInstance(statement.table, QualifiedTableName)
        self.assertEqual(statement.table.name, 'users')
        self.assertEqual(len(statement.set_assignments), 1)
        self.assertEqual(statement.set_assignments[0]['columns'], ['age'])
        self.assertIsInstance(statement.set_assignments[0]['expression'], Expression)
        self.assertEqual(str(statement.set_assignments[0]['expression']), '30')
        self.assertIsInstance(statement.where_expr, Expression)
        self.assertEqual(str(statement.where_expr), 'id = 1')
        self.assertIsNone(statement.from_clause)
        self.assertIsNone(statement.or_action)

    def test_update_with_multiple_assignments(self):
        """Test an UPDATE with multiple assignments separated by commas."""
        sql = "UPDATE products SET price = 99.99, stock = 50 WHERE category = 'electronics';"
        statement = self.parse_statement(sql)
        
        self.assertEqual(len(statement.set_assignments), 2)
        self.assertEqual(statement.set_assignments[0]['columns'], ['price'])
        self.assertEqual(str(statement.set_assignments[0]['expression']), '99.99')
        self.assertEqual(statement.set_assignments[1]['columns'], ['stock'])
        self.assertEqual(str(statement.set_assignments[1]['expression']), '50')
        self.assertEqual(str(statement.where_expr), "category = 'electronics'")

    def test_update_with_qualified_table_name(self):
        """Test an UPDATE statement with a schema.table format."""
        sql = "UPDATE schema.employees SET active = FALSE WHERE id = 123;"
        statement = self.parse_statement(sql)
        
        self.assertEqual(statement.table.schema, 'schema')
        self.assertEqual(statement.table.name, 'employees')

    def test_update_with_or_action(self):
        """Test an UPDATE statement with an OR action clause."""
        sql = "UPDATE OR IGNORE logs SET status = 'processed';"
        statement = self.parse_statement(sql)
        
        self.assertEqual(statement.or_action, 'IGNORE')
        self.assertEqual(statement.table.name, 'logs')
        self.assertEqual(len(statement.set_assignments), 1)

    def test_update_with_from_clause(self):
        """Test an UPDATE statement that includes a FROM clause."""
        sql = "UPDATE employees SET salary = t2.new_salary FROM new_salaries AS t2 WHERE employees.id = t2.employee_id;"
        statement = self.parse_statement(sql)
        
        self.assertIsInstance(statement.from_clause, TableOrSubQuery)
        self.assertEqual(statement.from_clause.name, 'new_salaries')
        self.assertEqual(statement.from_clause.alias, 't2')
        self.assertEqual(str(statement.set_assignments[0]['expression']), 't2.new_salary')
        self.assertEqual(str(statement.where_expr), 'employees.id = t2.employee_id')

    def test_update_with_returning_clause(self):
        """Test an UPDATE statement with a RETURNING clause."""
        sql = "UPDATE accounts SET balance = balance - 100 WHERE id = 123 RETURNING id, balance;"
        statement = self.parse_statement(sql)
        
        self.assertIsNotNone(statement.returning_exprs)
        self.assertEqual(len(statement.returning_exprs), 2)
        self.assertEqual(str(statement.returning_exprs[0]), 'id')
        self.assertEqual(str(statement.returning_exprs[1]), 'balance')

    def test_syntax_error_no_set(self):
        """Test for a missing SET keyword."""
        sql = "UPDATE users WHERE id = 1;"
        with self.assertRaisesRegex(ParsingException, "Expected SET"):
            self.parse_statement(sql)

    def test_syntax_error_invalid_or_action(self):
        """Test for an invalid keyword after OR."""
        sql = "UPDATE OR INVALID_ACTION users SET active = TRUE;"
        with self.assertRaisesRegex(ParsingException, "Expected ABORT, FAIL, IGNORE, REPLACE, or ROLLBACK after OR"):
            self.parse_statement(sql)
            
    def test_common_table_expression_not_supported(self):
        """Test that WITH clause correctly raises an exception."""
        sql = "WITH regional_sales AS (SELECT * FROM sales) UPDATE products SET price = 100;"
        with self.assertRaisesRegex(ParsingException, "Common Table Expressions"):
            self.parse_statement(sql)

if __name__ == '__main__':
    unittest.main()