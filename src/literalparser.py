
from dataclasses import dataclass
from typing import TypeAlias
from signednumberparser import SignedNumberParser
from sqltoken import TokenType
from baseparser import BaseParser, ParsingException

LiteralType: TypeAlias = int | float | bool | str | bytes | None

@dataclass
class Literal:
    """Container for constant value."""
    dtype: type
    value: LiteralType

class LiteralParser(BaseParser):
    """Parser for any constant values/literals."""
    def parse(self) -> Literal:
        """Parse contained tokens into a Literal.

        Currently can parse into types: int, float, bool, str, bytes, or NULL into None.

        Returns:
            Literal: Container of parsed value with value in proper datatype.
        """
        if self.valueMatches("NULL") or self.valueMatches("TRUE") or self.valueMatches("FALSE"):
            value = self.consume(TokenType.KEYWORD)
            bn_value =  BoolNullParser([value]).parse()
            return Literal(type(bn_value),  bn_value)

        if self.valueMatches("X") or self.valueMatches("x"):
            prefix = self.consume(TokenType.IDENTIFIER)
            hex_str = self.consume(TokenType.STRING_LITERAL)
            blob_value = BlobLiteralParser([prefix, hex_str]).parse()
            return Literal(bytes, blob_value)

        if self.typeMatches(TokenType.STRING_LITERAL):
            str_lit = self.consume(TokenType.STRING_LITERAL)
            str_value = StringLiteralParser([str_lit]).parse()
            return Literal(str, str_value)

        num_literals = []
        if self.typeMatches(TokenType.OPERATOR):
            num_literals.append(self.consume(TokenType.OPERATOR))
        num_literals.append(self.consume(TokenType.NUMBER_LITERAL))
        num_value = SignedNumberParser(num_literals).parse()
        return Literal(type(num_value), num_value)



class StringLiteralParser(BaseParser):
    """Parser for string literals. Value should be wrapped in 'single quotes' or "double quotes" """
    def parse(self) -> str:
        """Parse inner token to a string-typed value. Should be wrapped in 'x' or "y".

        Returns:
            str: Unwrapped literal value.
        """
        value = super().consume(TokenType.STRING_LITERAL).value
        if value[0] in {"'", '"'}:
            assert value[0] == value[-1]
            value = value[1:-1]
        return value


class BlobLiteralParser(BaseParser):
    """Parser for blob/binary literals"""
    def parse(self) -> bytes:
        """Parse hex-encoded data to its binary form.

        data should be formatted as one of the following:
        - x'data'
        - X'data'
        - x"data"
        - X"data"

        Returns:
            bytes: Hex data converted to binary datatype.
        """
        if not (self.valueMatches("x") or self.valueMatches("X")):
            raise ParsingException(f"attempted to parse BLOB object {self.tokens[0]} without leading x or X")
        super().consume(TokenType.IDENTIFIER)
        hex_string = super().consume(TokenType.STRING_LITERAL).value
        assert hex_string[0] in {"'", '"'}
        assert hex_string[0] == hex_string[-1]
        hex_seq = hex_string[1:-1]
        return bytes.fromhex(hex_seq)


class BoolNullParser(BaseParser):
    """Parser for TRUE and FALSE into binary values and NULL into None"""
    def parse(self) -> bool | None:
        """Parse TRUE, FALSE, and NULL keywords into their respective Python constant.

        Returns:
            bool | None: Parsed value in its proper datatype.
        """
        if not (self.valueMatches("TRUE") or self.valueMatches("FALSE") or self.valueMatches("NULL")):
            raise ParsingException(f"expected TRUE/FALSE/NULL, received {self.tokens[0]}")
        value = self.consume(TokenType.KEYWORD).value
        match value:
            case "TRUE":
                return True
            case "FALSE":
                return False
            case "NULL":
                return None

