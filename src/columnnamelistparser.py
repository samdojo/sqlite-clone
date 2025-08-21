from typing import List

from baseparser import BaseParser, ParsingException
from sqltoken import TokenType


class ColumnNameListParser(BaseParser):

    def parse(self) -> List[str]:
        """Parse a list of column names."""
        column_names: List[str] = []
        super().consume(TokenType.LPAREN)
        while True:
            if self.typeMatches(TokenType.IDENTIFIER):
                token = super().consume(TokenType.IDENTIFIER)
                column_names.append(token.value)
                if self.typeMatches(TokenType.COMMA):
                    self._handle_comma()
                elif self.typeMatches(TokenType.RPAREN):
                    super().consume(TokenType.RPAREN)
                    return column_names
                else:
                    raise ParsingException(
                        f"Unexpected token after column name, got {self.tokens[0]}"
                    )
            else:
                raise ParsingException(
                    f"Expected identifier or comma, got {self.tokens[0]}"
                )

    def _handle_comma(self) -> None:
        super().consume(TokenType.COMMA)
        if not self.typeMatches(TokenType.IDENTIFIER):
            raise ParsingException(
                f"Unexpected token after comma, got {self.tokens[0]}"
            )
