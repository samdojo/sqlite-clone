from typing import List

from baseparser import BaseParser, ParsingException
from sqltoken import TokenType


class ColumnNameListParser(BaseParser):

    def parse(self) -> List[str]:
        """Parse a list of column names."""
        column_names: List[str] = []
        if not self.typeMatches(TokenType.LPAREN):
            raise ParsingException(
                f"Column list must be in parenthesis, got {self.tokens[0]}"
            )
        super().consume(TokenType.LPAREN)

        if not self.typeMatches(TokenType.IDENTIFIER):
            raise ParsingException(
                f"Column list must start with a column name, got {self.tokens[0]}"
            )
        while True:
            if self.typeMatches(TokenType.IDENTIFIER):
                column_names.append(self._handle_column_name())

            if self.typeMatches(TokenType.COMMA):
                self._handle_comma()
            elif self.typeMatches(TokenType.RPAREN):
                break
            else:
                raise ParsingException(
                    f"Unexpected token after column name, got {self.tokens[0]}. Expected comma or parenthesis."
                )
        super().consume(TokenType.RPAREN)
        return column_names

    def _handle_column_name(self) -> str:
        token = super().consume(TokenType.IDENTIFIER)
        return token.value

    def _handle_comma(self) -> None:
        super().consume(TokenType.COMMA)
        if not self.typeMatches(TokenType.IDENTIFIER):
            raise ParsingException(
                f"Unexpected token after comma, got {self.tokens[0]}"
            )
