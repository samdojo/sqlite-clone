from typing import List, Optional
from sqltoken import Token, TokenType

class ParsingException(Exception):
    pass

class BaseParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def typeMatches(self, tokenType: TokenType):
        if not self.tokens:
            raise ParsingException('no token to match with')
        return self.tokens[0].type == tokenType
    
    def valueMatches(self, value: str):
        if not self.tokens:
            raise ParsingException('no token to match with')
        return self.tokens[0].value == value

    def consume(self, type: TokenType, value: Optional[str] = None) -> Token:
        if not self.tokens:
            raise ParsingException('no token to consume')
        current_token = self.tokens[0]
        if self.typeMatches(type):
            if value is None:
                return self.tokens.pop(0)
            else:
                if self.valueMatches(value):
                    return self.tokens.pop(0)
                else:
                    raise ParsingException(f'unexpected token value {current_token.value} (expected {value})')
        else:
            raise ParsingException(f'unexpected token type {current_token.type} (expected {type})')
