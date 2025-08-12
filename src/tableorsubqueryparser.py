from dataclasses import dataclass
from parser import Parser
from typing import Optional, Union

from baseparser import BaseParser, ParsingException
from sqltoken import TokenType
from statements import SelectStatement


@dataclass
class Table:
    table_name: str
    schema_name: Optional[str]
    table_alias: Optional[str]


@dataclass
class Subquery:
    select_statement: SelectStatement


class TableOrSubqueryParser(BaseParser):
    def parse(self) -> Union[Table, Subquery]:

        if self.typeMatches(TokenType.IDENTIFIER):
            schema_name = None
            table_name = None
            table_alias = None

            token = super().consume(TokenType.IDENTIFIER)

            if self.typeMatches(TokenType.EOF):
                return Table(token.value, None, None)
            else:
                schema_name = token.value

            if self.typeMatches(TokenType.DOT):
                super().consume(TokenType.DOT)

            if self.typeMatches(TokenType.IDENTIFIER):
                token = super().consume(TokenType.IDENTIFIER)
                table_name = token.value
            else:
                raise ParsingException("Expected table name after dot")

            if self.typeMatches(TokenType.EOF):
                return Table(table_name, schema_name, None)

            if self.typeMatches(TokenType.KEYWORD):
                if not self.valueMatches("AS"):
                    raise ParsingException(
                        f"Unknown keyword {token.value} after table name"
                    )
                super().consume(TokenType.KEYWORD)

                if self.typeMatches(TokenType.IDENTIFIER):
                    token = super().consume(TokenType.IDENTIFIER)
                    table_alias = token.value
                else:
                    raise ParsingException("Expected table alias after AS")

            return Table(table_name, schema_name, table_alias)

        elif self.typeMatches(TokenType.LPAREN):
            super().consume(TokenType.LPAREN)

            select_parser = Parser(self.tokens)
            select_statement = select_parser.parseSelectStatementIfMatches()
            if select_statement is None:
                raise ParsingException("Expected select statement after parenthesis")
            super().consume(TokenType.RPAREN)
            return Subquery(select_statement)
