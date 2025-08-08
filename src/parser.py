from typing import Optional
from signednumberparser import SignedNumberParser
from baseparser import BaseParser
from statements import SelectStatement

# any 'parseXxxIfMatches()' function should catch any error and return None
# any other 'parse()' function should return the appropriate data object
class Parser(BaseParser):
    # parse any statement
    def parse(self):
        statement = self.parseSelectStatementIfMatches()
        if statement is not None:
            return statement

        #statment = self.parseInsertStatementIfMatches()
        if statement is not None:
            return statement

        #statment = self.parseCreateTableStatementIfMatches()
        if statement is not None:
            return statement

    def parseNumericLiteralIfMatches(self) -> Optional[int]:
        try:
            parser = SignedNumberParser()
            return parser.parse()
        except:
            return None

    def parseSelectStatementIfMatches(self) -> Optional[SelectStatement]:
         # TODO
         return None
