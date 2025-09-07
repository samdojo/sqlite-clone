from typing import Optional, List
from baseparser import BaseParser, ParsingException
from sqltoken import TokenType
from statements import InsertStatement, Expression
from qualifiedtablenameparser import QualifiedTableNameParser
from columnnamelistparser import ColumnNameListParser
from expressionparser import ExpressionParser


class InsertStatementParser(BaseParser):
    """
    Parser for the basic INSERT ... VALUES (...) form (single row).
    """

    def _consume_keyword(self, expected: str) -> None:
        if not self.typeMatches(TokenType.KEYWORD) or not self.valueMatches(expected):
            raise ParsingException(f"Expected {expected}")
        self.consume(TokenType.KEYWORD)  # consume the keyword

    def parse(self) -> InsertStatement:
        # INSERT
        self._consume_keyword("INSERT")

        # INTO
        self._consume_keyword("INTO")

        # target table: [schema.]table [AS alias]
        qtn = QualifiedTableNameParser(self.tokens).parse()

        # optional column list:
        column_names: Optional[List[str]] = None
        if self.typeMatches(TokenType.LPAREN):
            column_names = ColumnNameListParser(self.tokens).parse()

        # VALUES
        self._consume_keyword("VALUES")

        # parenthesized value list
        if not self.typeMatches(TokenType.LPAREN):
            raise ParsingException("Expected '(' after VALUES")

        values_expr: Expression = ExpressionParser(self.tokens).parse()
        if values_expr.route != 8 or values_expr.expr_array is None:
            raise ParsingException("Expected a parenthesized value list")

        values = values_expr.expr_array

        # Build the statement (leave any trailing tokens unconsumed)
        return InsertStatement(
            table_name=qtn.table_name,
            schema_name=qtn.schema_name,
            alias=qtn.alias,
            column_names=column_names,
            values=values,
        )
