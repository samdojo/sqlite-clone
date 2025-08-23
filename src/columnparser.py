# columnparser.py
from typing import List, Optional
from statements import Column
from baseparser import BaseParser, ParsingException
from sqltoken import Token, TokenType


class ColumnParser(BaseParser):
    def __init__(self, tokens: List[Token]):
        super().__init__(tokens)

    def parse(self) -> Column:
        if not self.tokens:
            raise ParsingException("No tokens to parse")

        # first token = column name
        name_token = self.tokens.pop(0)
        name = name_token.value

        # second token (optional) = type
        col_type = None
        if self.tokens and self.tokens[0].type == TokenType.IDENTIFIER:
            col_type = self.tokens.pop(0).value

        # defaults
        default_value: Optional[str] = None
        nullable = True
        primary_key = False
        unique = False
        constraints: List[str] = []

        # process remaining tokens
        while self.tokens:
            token = self.tokens.pop(0)
            tok_val = token.value.upper()

            if tok_val == "DEFAULT" and self.tokens:
                default_value = self.tokens.pop(0).value
            elif tok_val == "NOT" and self.tokens and self.tokens[0].value.upper() == "NULL":
                self.tokens.pop(0)
                nullable = False
            elif tok_val == "PRIMARY" and self.tokens and self.tokens[0].value.upper() == "KEY":
                self.tokens.pop(0)
                primary_key = True
                nullable = False  # PRIMARY KEY implies NOT NULL
            elif tok_val == "UNIQUE":
                unique = True
            else:
                constraints.append(tok_val)

        return Column(
            name=name,
            type=col_type,
            nullable=nullable,
            default=default_value,
            primary_key=primary_key,
            unique=unique,
            constraints=constraints
        )
