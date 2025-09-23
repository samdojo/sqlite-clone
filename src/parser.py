from typing import Optional

from baseparser import BaseParser
from insertparser import InsertStatementParser
from selectparser import SelectStatementParser
from signednumberparser import SignedNumberParser
from sqltoken import TokenType
from statements import InsertStatement, SelectStatement


# any 'parseXxxIfMatches()' function should catch any error and return None
# any other 'parse()' function should return the appropriate data object
class Parser(BaseParser):
    # parse any statement
    def parse(self):
        statement = self.parseSelectStatementIfMatches()
        if statement is not None:
            return statement

        statement = self.parseInsertStatementIfMatches()
        if statement is not None:
            return statement

        # statment = self.parseCreateTableStatementIfMatches()
        if statement is not None:
            return statement

    def parseNumericLiteralIfMatches(self) -> Optional[int]:
        try:
            parser = SignedNumberParser()
            return parser.parse()
        except:
            return None

    def parseSelectStatementIfMatches(self) -> Optional[SelectStatement]:
        try:
            if not self.typeMatches(TokenType.KEYWORD) or not self.valueMatches(
                "SELECT"
            ):
                return None
            parser = SelectStatementParser(self.tokens)
            return parser.parse()
        except:
            return None

    def parseInsertStatementIfMatches(self) -> Optional[InsertStatement]:
        try:
            if not self.typeMatches(TokenType.KEYWORD) or not self.valueMatches(
                "INSERT"
            ):
                return None
            parser = InsertStatementParser(self.tokens)
            return parser.parse()
        except:
            return None
