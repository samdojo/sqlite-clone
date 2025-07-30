from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    KEYWORD = "KEYWORD"

    IDENTIFIER = "IDENTIFIER"
    STRING_LITERAL = "STRING_LITERAL"
    NUMBER_LITERAL = "NUMBER_LITERAL"

    OPERATOR = "OPERATOR"
    COMPARISON = "COMPARISON"

    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"

    LPAREN = "LPAREN"
    RPAREN = "RPAREN"

    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"

    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

@dataclass
class Token:
    type: TokenType
    value: str
