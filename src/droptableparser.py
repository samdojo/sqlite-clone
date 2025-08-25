from baseparser import BaseParser
from statements import DropTableStatement
from sqltoken import TokenType
from baseparser import ParsingException

class DropTableParser(BaseParser):
    def parse(self) -> DropTableStatement:
        # Expect "DROP"
        if not self.valueMatches("DROP"):
            raise ParsingException("Expected DROP")
        super().consume(TokenType.KEYWORD)

        # Expect "TABLE"
        if not self.valueMatches("TABLE"):
            raise ParsingException("Expected TABLE")
        super().consume(TokenType.KEYWORD)

        # Optional "IF EXISTS"
        if_exists = False
        if self.valueMatches("IF"):
            super().consume(TokenType.KEYWORD)
            if self.valueMatches("EXISTS"):
                super().consume(TokenType.KEYWORD)
                if_exists = True

        # Table name (optionally with schema)
        schema_name = None
        table_token = super().consume(TokenType.IDENTIFIER)
        table_name = table_token.value

        if self.valueMatches("."):
            super().consume(TokenType.DOT)
            schema_name = table_name
            table_token = super().consume(TokenType.IDENTIFIER)
            table_name = table_token.value

        return DropTableStatement(
            table_name=table_name,
            schema_name=schema_name,
            if_exists=if_exists
        )
