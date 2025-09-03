from typing import List, Optional

from baseparser import BaseParser, ParsingException
from sqltoken import TokenType
from statements import UpdateStatement
from qualifiedtablenameparser import QualifiedTableNameParser
from columnnamelistparser import ColumnNameListParser
from expressionparser import ExpressionParser
from tableorsubqueryparser import TableOrSubQueryParser


class UpdateParser(BaseParser):
    """
    Parser for UPDATE statements (AST only, no execution).
    """

    def parse(self) -> UpdateStatement:
        # --- WITH clause, not supported) ---
        if self.valueMatches("WITH"):
            raise ParsingException("Common Table Expressions (WITH clause) not supported yet")

        # --- UPDATE keyword ---
        if not self.valueMatches("UPDATE"):
            raise ParsingException("Expected UPDATE")
        super().consume(TokenType.KEYWORD)

        # --- OR action ---
        or_action = None
        if self.valueMatches("OR"):
            super().consume(TokenType.KEYWORD)
            if self.valueMatches("ABORT"):
                or_action = "ABORT"
            elif self.valueMatches("FAIL"):
                or_action = "FAIL"
            elif self.valueMatches("IGNORE"):
                or_action = "IGNORE"
            elif self.valueMatches("REPLACE"):
                or_action = "REPLACE"
            elif self.valueMatches("ROLLBACK"):
                or_action = "ROLLBACK"
            else:
                raise ParsingException(
                    "Expected ABORT, FAIL, IGNORE, REPLACE, or ROLLBACK after OR"
                )
            super().consume(TokenType.KEYWORD)

        # --- Qualified table name ---
        table_parser = QualifiedTableNameParser(self.tokens[self.pos:])
        table = table_parser.parse()
        consumed = len(self.tokens[self.pos:]) - len(table_parser.tokens)
        self.pos += consumed

        # --- SET clause ---
        if not self.valueMatches("SET"):
            raise ParsingException("Expected SET in UPDATE statement")
        super().consume(TokenType.KEYWORD)

        set_assignments = []
        while True:
            if self.valueMatches("("):
                # Column-name-list = row-value
                col_parser = ColumnNameListParser(self.tokens[self.pos:])
                column_names = col_parser.parse()
                consumed = len(self.tokens[self.pos:]) - len(col_parser.tokens)
                self.pos += consumed

                if not self.valueMatches("="):
                    raise ParsingException("Expected '=' after column name list")
                super().consume(TokenType.EQ)

                expr = self._parse_expression()
                set_assignments.append({'columns': column_names, 'expression': expr, 'is_column_list': True})
            else:
                # Single column = expression
                if not self.typeMatches(TokenType.IDENTIFIER):
                    raise ParsingException("Expected column name in SET assignment")
                column_name = super().consume(TokenType.IDENTIFIER).value

                if not self.valueMatches("="):
                    raise ParsingException("Expected '=' in SET assignment")
                super().consume(TokenType.EQ)

                expr = self._parse_expression()
                set_assignments.append({'columns': [column_name], 'expression': expr, 'is_column_list': False})

            if self.typeMatches(TokenType.COMMA):
                super().consume(TokenType.COMMA)
                continue
            break

        # --- FROM clause ---
        from_clause = None
        if self.valueMatches("FROM"):
            super().consume(TokenType.KEYWORD)
            from_parser = TableOrSubQueryParser(self.tokens[self.pos:])
            from_clause = from_parser.parse()
            consumed = len(self.tokens[self.pos:]) - len(from_parser.tokens)
            self.pos += consumed

        # --- WHERE clause ---
        where_expr = None
        if self.valueMatches("WHERE"):
            super().consume(TokenType.KEYWORD)
            where_expr = self._parse_expression()

        # --- RETURNING clause ---
        returning_exprs = None
        if self.valueMatches("RETURNING"):
            super().consume(TokenType.KEYWORD)
            returning_exprs = self._parse_returning_list()

        return UpdateStatement(
            table=table,
            set_assignments=set_assignments,
            from_clause=from_clause,
            where_expr=where_expr,
            returning_exprs=returning_exprs,
            or_action=or_action
        )

    # --- Helpers ---

    def _parse_expression(self):
        """Parse a single expression (delegates to ExpressionParser)."""
        parser = ExpressionParser(self.tokens[self.pos:])
        expr = parser.parse()
        consumed = len(self.tokens[self.pos:]) - len(parser.tokens)
        self.pos += consumed
        return expr

    def _parse_returning_list(self):
        """Parse a comma-separated list of RETURNING expressions."""
        expressions = []
        while True:
            expr = self._parse_expression()
            expressions.append(expr)
            if self.typeMatches(TokenType.COMMA):
                super().consume(TokenType.COMMA)
                continue
            break
        return expressions

    def _parse_common_table_expression_list(self, recursive: bool):
        """CTEs not supported yet."""
        raise ParsingException("Common Table Expressions (WITH clause) are not supported yet")
