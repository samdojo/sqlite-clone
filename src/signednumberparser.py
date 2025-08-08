from sqltoken import TokenType
from baseparser import BaseParser

class SignedNumberParser(BaseParser):
    def parse(self) -> int | float:
        negative = False
        if self.typeMatches(TokenType.OPERATOR):
            if self.valueMatches('-'):
                negative = True
                super().consume(TokenType.OPERATOR)
            elif self.valueMatches('+'):
                super().consume(TokenType.OPERATOR)

        value = super().consume(TokenType.NUMBER_LITERAL).value
        if '.' in value:
            value = float(value)
        else:
            value = int(value)
        if negative:
            value *= -1
        return value
