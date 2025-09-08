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

    def parse(self) -> InsertStatement:
        # INSERT
        self.consume(TokenType.KEYWORD, "INSERT")
        # INTO
        self.consume(TokenType.KEYWORD, "INTO")

        # target table: [schema.]table [AS alias]
        table_ref = QualifiedTableNameParser(self.tokens).parse()

        # optional column list:
        column_names: Optional[List[str]] = None
        if self.typeMatches(TokenType.LPAREN):
            column_names = ColumnNameListParser(self.tokens).parse()

        # VALUES
        self.consume(TokenType.KEYWORD, "VALUES")

        # parenthesized value list
        if not self.typeMatches(TokenType.LPAREN):
            got = self.tokens[0] if self.tokens else None
            raise ParsingException(f"Expected '(' after VALUES, got {got}")

        values_expr: Expression = ExpressionParser(self.tokens).parse()
        if values_expr.route != 8 or values_expr.expr_array is None:
            raise ParsingException("Expected a parenthesized value list")

        values = values_expr.expr_array

        # Build the statement (leave any trailing tokens unconsumed)
        return InsertStatement(
            table_name=table_ref.table_name,
            schema_name=table_ref.schema_name,
            alias=table_ref.alias,
            column_names=column_names,
            values=values
        )
