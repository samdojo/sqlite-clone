from typing import List, Optional
from statements import SelectStatement
from baseparser import BaseParser, ParsingException
from sqltoken import Token, TokenType


class SelectParser(BaseParser):
    def __init__(self, tokens: List[Token]):
        super().__init__(tokens)

    def parse(self) -> SelectStatement:
        if not self.tokens:
            raise ParsingException("No tokens to parse")

        # Expect SELECT keyword
        if not (self.typeMatches(TokenType.KEYWORD) and self.valueMatches("SELECT")):
            raise ParsingException("Expected SELECT")
        self.consume(TokenType.KEYWORD, "SELECT")

        # Parse columns
        columns: List[str] = []
        while self.tokens and not (self.typeMatches(TokenType.KEYWORD) and self.valueMatches("FROM")):
            token = self.tokens.pop(0)
            if token.value != ",":
                columns.append(token.value.strip())

        if not columns:
            raise ParsingException("No columns specified in SELECT")

        # Expect FROM keyword
        if not (self.typeMatches(TokenType.KEYWORD) and self.valueMatches("FROM")):
            raise ParsingException("Expected FROM")
        self.consume(TokenType.KEYWORD, "FROM")

        # Parse table name
        if not self.tokens or not self.typeMatches(TokenType.IDENTIFIER):
            raise ParsingException("Expected table name")
        table = self.consume(TokenType.IDENTIFIER).value.strip()

        # Optional WHERE clause
        where_clause: Optional[str] = None
        if self.tokens and self.typeMatches(TokenType.KEYWORD) and self.valueMatches("WHERE"):
            self.consume(TokenType.KEYWORD, "WHERE")

            # Collect remaining token values as WHERE expression
            where_tokens = []
            while self.tokens:
                token = self.tokens.pop(0)
                if token.value.strip():  # ignore empty or whitespace tokens
                    where_tokens.append(token.value)
            where_clause = " ".join(where_tokens).strip()

        return SelectStatement(
            columns=columns,
            table=table,
            where=where_clause
        )
