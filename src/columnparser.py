from typing import List, Optional

from baseparser import BaseParser, ParsingException
from sqltoken import Token, TokenType
from statements import Column


class ColumnParser(BaseParser):
    def __init__(self, tokens: List[Token]):
        super().__init__(tokens)

    def parse(self) -> Column:
        if not self.tokens:
            raise ParsingException("No tokens to parse")

        # first token = column name
        name_token = self.consume(TokenType.IDENTIFIER)
        name = name_token.value

        # optional type
        col_type = None
        if self.tokens and (
            self.typeMatches(TokenType.IDENTIFIER)
            or self.typeMatches(TokenType.KEYWORD)
        ):
            col_type = self.consume(self.tokens[0].type).value

            # handle type args in parentheses (e.g. VARCHAR(255), DECIMAL(10,2))
            if self.tokens and self.valueMatches("("):
                args = [self.consume(TokenType.LPAREN, "(").value]
                while self.tokens and not self.valueMatches(")"):
                    args.append(self.consume(self.tokens[0].type).value)
                if self.tokens and self.valueMatches(")"):
                    args.append(self.consume(TokenType.RPAREN, ")").value)
                col_type += "".join(args)

        # defaults
        default_value: Optional[str] = None
        nullable = True
        primary_key = False
        unique = False
        constraints: List[str] = []

        # process remaining tokens
        while self.tokens:
            token = self.tokens[0]
            tok_val = token.value.upper()

            # stop at column separator
            if token.value in {",", ")"}:
                break

            if tok_val == "DEFAULT":
                self.consume(TokenType.KEYWORD, "DEFAULT")
                if self.tokens:
                    default_value = self.consume(self.tokens[0].type).value
            elif tok_val == "NOT":
                self.consume(TokenType.KEYWORD, "NOT")
                if self.tokens and self.valueMatches("NULL"):
                    self.consume(TokenType.KEYWORD, "NULL")
                    nullable = False
            elif tok_val == "PRIMARY":
                self.consume(TokenType.KEYWORD, "PRIMARY")
                if self.tokens and self.valueMatches("KEY"):
                    self.consume(TokenType.KEYWORD, "KEY")
                    primary_key = True
                    nullable = False  # PRIMARY KEY implies NOT NULL
            elif tok_val == "UNIQUE":
                self.consume(TokenType.KEYWORD, "UNIQUE")
                unique = True
            else:
                constraints.append(tok_val)
                self.consume(token.type)  # consume unknown token

        return Column(
            name=name,
            type=col_type,
            nullable=nullable,
            default=default_value,
            primary_key=primary_key,
            unique=unique,
            constraints=constraints,
        )
