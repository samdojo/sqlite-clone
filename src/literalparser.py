
from signednumberparser import SignedNumberParser
from sqltoken import TokenType
from baseparser import BaseParser, ParsingException
from statements import Literal


class LiteralParser(BaseParser):
    """Parser for any constant values/literals."""
    def parse(self) -> Literal:
        """Parse contained tokens into a Literal.

        Currently can parse into types: int, float, bool, str, bytes, or NULL into None.

        Returns:
            Literal: Container of parsed value with value in proper datatype.
        """
        if self.valueMatches("NULL") or self.valueMatches("TRUE") or self.valueMatches("FALSE"):
            bn_value =  BoolNullParser(self.tokens).parse()
            return Literal(type(bn_value),  bn_value)

        if self.valueMatches("X") or self.valueMatches("x"):
            blob_value = BlobLiteralParser(self.tokens).parse()
            return Literal(bytes, blob_value)

        if self.typeMatches(TokenType.STRING_LITERAL):
            str_value = StringLiteralParser(self.tokens).parse()
            return Literal(str, str_value)

        num_value = SignedNumberParser(self.tokens).parse()
        return Literal(type(num_value), num_value)



class StringLiteralParser(BaseParser):
    """Parser for string literals. Value should be wrapped in 'single quotes' or "double quotes" """
    def parse(self) -> str:
        """Parse inner token to a string-typed value. Should be wrapped in 'x' or "y".

        Returns:
            str: Unwrapped literal value.
        """
        value = self.consume(TokenType.STRING_LITERAL).value
        if value[0] in {"'", '"'}:
            if value[0] != value[-1]:
                raise ParsingException(f"string literal {value} has mismatching quotes")
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
        self.consume(TokenType.IDENTIFIER)
        hex_string = self.consume(TokenType.STRING_LITERAL).value
        if hex_string[0] not in {"'", '"'}:
            raise ParsingException(f"BLOB literal {hex_string} needs matching quotes around data")
        if hex_string[0] != hex_string[-1]:
            raise ParsingException(f"BLOB literal {hex_string} needs matching quotes around data")
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

