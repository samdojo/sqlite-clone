from typing import Optional
from baseparser import BaseParser, ParsingException
from sqltoken import TokenType
from statements import Table


class QualifiedTableNameParser(BaseParser):
    """
    Parser for qualified-table-name in UPDATE statements.

    """

    def parse(self) -> Table:
        """
        Parses: [schema.]table [AS alias]
        Returns:
            Table(table_name, schema_name, alias)
        """
        if not self.typeMatches(TokenType.IDENTIFIER):
            raise ParsingException("Expected table name (or schema) after UPDATE")

        # Identifier
        first = super().consume(TokenType.IDENTIFIER)
        schema_name: Optional[str] = None
        table_name: str = first.value

        # SCHEMA.TABLE
        if self.typeMatches(TokenType.DOT):
            super().consume(TokenType.DOT)
            schema_name = first.value
            if not self.typeMatches(TokenType.IDENTIFIER):
                raise ParsingException("Expected table name after 'schema.'")
            table_name = super().consume(TokenType.IDENTIFIER).value

        # ALIAS
        alias = self._parse_alias_if_exists(require_as=False)
        return Table(table_name, schema_name, alias)

    def _parse_alias_if_exists(self, require_as: bool = False) -> Optional[str]:
        """
        Parses an alias (if present)
        """
        # If AS is required
        if self.typeMatches(TokenType.KEYWORD) and self.valueMatches("AS"):
            super().consume(TokenType.KEYWORD)  # AS
            if not self.typeMatches(TokenType.IDENTIFIER):
                raise ParsingException("Expected identifier after AS")
            return super().consume(TokenType.IDENTIFIER).value

        # If AS is not required
        if not require_as and self.typeMatches(TokenType.IDENTIFIER):
            return super().consume(TokenType.IDENTIFIER).value

        return None
