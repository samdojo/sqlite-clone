from typing import List

from baseparser import BaseParser, ParsingException
from columnparser import ColumnParser
from sqltoken import TokenType
from statements import Column, CreateTableStatement


class CreateTableParser(BaseParser):
    """Parser for CREATE TABLE statements."""

    def parse(self) -> CreateTableStatement:
        """Parse contained tokens into a CreateTable.

        Returns:
            CreateTableStatement: Container of parsed table name and column names.
        """
        result = CreateTableStatement(table_name="", schema_name=None, columns=[])

        self._consume_keywords()
        result.table_name, result.schema_name = self._parse_table_name()
        self.consume(TokenType.LPAREN)
        result.columns = self._parse_columns()
        return result

    def _consume_keywords(self) -> None:
        if not self.typeMatches(TokenType.KEYWORD) and not self.valueMatches("CREATE"):
            raise ParsingException(
                f"Unexpected token {self.tokens[0]} at the beginning of the list"
            )
        super().consume(TokenType.KEYWORD)
        if not self.typeMatches(TokenType.KEYWORD) and not self.valueMatches("TABLE"):
            raise ParsingException(
                f"Unexpected token {self.tokens[0]} at the beginning of the list"
            )
        super().consume(TokenType.KEYWORD)

    def _parse_table_name(self) -> tuple[str, str]:
        if not self.typeMatches(TokenType.IDENTIFIER):
            raise ParsingException(
                f"Unexpected token {self.tokens[0]} at the beginning of the list"
            )
        first_token = super().consume(TokenType.IDENTIFIER)
        schema_name = None
        table_name = first_token.value
        if self.typeMatches(TokenType.DOT):
            super().consume(TokenType.DOT)
            schema_name = first_token.value
            if not self.typeMatches(TokenType.IDENTIFIER):
                raise ParsingException(f"Unexpected token {self.tokens[0]} after DOT")

            second_token = super().consume(TokenType.IDENTIFIER)
            table_name = second_token.value
        return table_name, schema_name

    def _parse_columns(self) -> List[Column]:
        result: List[Column] = []
        column_parser = ColumnParser(self.tokens)
        while True:
            if self.tokens:
                result.append(column_parser.parse())
                if self.tokens and self.tokens[0].type == TokenType.COMMA:
                    super().consume(TokenType.COMMA)
                elif self.tokens and self.tokens[0].type == TokenType.RPAREN:
                    super().consume(TokenType.RPAREN)
                    break
                else:
                    raise ParsingException(
                        f"Unexpected token {self.tokens[0]} at the beginning of the list"
                    )
            else:
                break
        return result
