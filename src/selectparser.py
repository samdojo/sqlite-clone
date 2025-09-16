from typing import List, Optional
from statements import SelectStatement
from baseparser import BaseParser, ParsingException
from sqltoken import TokenType


class SelectParser(BaseParser):
    def parse(self) -> SelectStatement:
        if not self.tokens:
            raise ParsingException("No tokens to parse")

        # Expect SELECT keyword
        if not (self.typeMatches(TokenType.KEYWORD) and self.valueMatches("SELECT")):
            raise ParsingException("Expected SELECT")
        self.consume(TokenType.KEYWORD, "SELECT")

        # Parse columns
        columns: List[str] = []
        expect_column = True  # True if we expect a column next, False if we expect a comma

        while self.tokens and not (self.typeMatches(TokenType.KEYWORD) and self.valueMatches("FROM")):
            if self.typeMatches(TokenType.COMMA):
                if expect_column:
                    # Comma without a preceding column
                    raise ParsingException(f"Unexpected comma at {self.tokens[0]}")
                self.consume(TokenType.COMMA)
                expect_column = True
                continue

            if self.valueMatches("*"):
                if not expect_column:
                    raise ParsingException(f"Missing comma before '*' at {self.tokens[0]}")
                columns.append(self.consume(TokenType.OPERATOR, "*").value)
                expect_column = False
                continue

            if not self.typeMatches(TokenType.IDENTIFIER):
                raise ParsingException(f"Unexpected token in column list: {self.tokens[0]}")

            if not expect_column:
                raise ParsingException(f"Missing comma before {self.tokens[0].value}")
            columns.append(self.consume(TokenType.IDENTIFIER).value)
            expect_column = False

        if not columns:
            raise ParsingException("No columns specified in SELECT")
        if expect_column:
            # If we are still expecting a column but reached FROM, that means trailing comma
            raise ParsingException("Trailing comma without a column before FROM")

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
            where_tokens = [token.value for token in self.tokens if token.value.strip()]
            where_clause = " ".join(where_tokens).strip()
            self.tokens.clear()

        return SelectStatement(
            columns=columns,
            table=table,
            where=where_clause
        )
