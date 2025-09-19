from signednumberparser import SignedNumberParser
from sqltoken import TokenType
from statements import TypeAffinities, TypeName
from baseparser import BaseParser, ParsingException


class TypeNameParser(BaseParser):
    def parse(self) -> TypeName:
        # Retrive type name, arbitrary identifier or potentially keyword
        if self.typeMatches(TokenType.IDENTIFIER):
            name = self.consume(TokenType.IDENTIFIER).value
        elif self.typeMatches(TokenType.KEYWORD):
            name = self.consume(TokenType.KEYWORD).value
        else:
            raise ParsingException(
                f"type name {self.tokens[0].value} must be an IDENTIFIER or KEYWORD token, found {self.tokens[0].type} token"
            )
        # Parse capacity/numeric args if present
        numeric_arg1: None | int | float = None
        numeric_arg2: None | int | float = None
        if self.typeMatches(TokenType.LPAREN):
            self.consume(TokenType.LPAREN)
            numeric_arg1 = SignedNumberParser(self.tokens).parse()
            if self.typeMatches(TokenType.COMMA):
                self.consume(TokenType.COMMA)
                numeric_arg2 = SignedNumberParser(self.tokens).parse()
            self.consume(TokenType.RPAREN)
        numeric_args = (numeric_arg1, numeric_arg2)
        # Determine type affinity from name
        if "INT" in name.upper():
            type_affinity = TypeAffinities.INTEGER
        elif "CHAR" in name.upper() or "CLOB" in name.upper() or "TEXT" in name.upper():
            type_affinity = TypeAffinities.TEXT
        elif "BLOB" in name.upper():
            type_affinity = TypeAffinities.BLOB
        elif "REAL" in name.upper() or "FLOA" in name.upper() or "DOUB" in name.upper():
            type_affinity = TypeAffinities.REAL
        else:
            type_affinity = TypeAffinities.NUMERIC

        return TypeName(name, numeric_args, type_affinity)
