from typing import List
from baseparser import BaseParser, ParsingException
from sqltoken import Token, TokenType
from tableorsubqueryparser import TableOrSubqueryParser
from statements import UpdateTableStatement, Table

class UpdateParser(BaseParser):
    def __init__(self, tokens: List[Token]):
        super().__init__(tokens)

    def parse(self) -> UpdateTableStatement:
        self.consume(TokenType.KEYWORD, "UPDATE")

        table_parser = TableOrSubqueryParser(self.tokens)
        table_or_subquery = table_parser.parse()

        # For now, we only expect a single table, not a list or subqueries
        if not table_or_subquery or not isinstance(table_or_subquery[0], Table):
            raise ParsingException("Expected a table name after UPDATE")

        table = table_or_subquery[0]

        return UpdateTableStatement(table=table)