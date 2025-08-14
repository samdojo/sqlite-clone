from dataclasses import dataclass
from parser import Parser
from typing import List, Optional, Union

from baseparser import BaseParser, ParsingException
from sqltoken import TokenType
from statements import SelectStatement


@dataclass
class Table:
    """
    Table container to store the table name, schema name and alias.
    """

    table_name: str
    schema_name: Optional[str]
    table_alias: Optional[str]


class TableOrSubqueryParser(BaseParser):
    """
    Parser for table or subquery.

    """

    def parse(self) -> Union[Table, List[Table], SelectStatement]:
        """
        Parse tokens and return a table, a list of tables or a subquery.

        A table contains a table name with an optional schema name and an optional alias.
        Multiple tables can be enclosed in parentheses.
        A subquery is a SELECT statement enclosed in parentheses.

        Returns:
            Union[Table, List[Table], SelectStatement]: A table, a list of tables or a subquery.

        Raises:
            ParsingException: If the input tokens do not match the expected format.
        """

        if self.typeMatches(TokenType.IDENTIFIER):
            return self._parse_table()

        elif self.typeMatches(TokenType.LPAREN):
            return self._parse_parenthesis_content()

    def _parse_table(self) -> Table:
        """
        Parse a table, its schema name and alias if exists.

        Examples:
        - table_name
        - schema_name.table_name
        - schema_name.table_name AS table_alias

        Returns:
            Table: A table object.
        """
        schema_name = None
        table_name = None
        table_alias = None

        token = super().consume(TokenType.IDENTIFIER)

        if (
            self.typeMatches(TokenType.EOF)
            or self.typeMatches(TokenType.RPAREN)
            or self.typeMatches(TokenType.COMMA)
        ):
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

        if self.typeMatches(TokenType.EOF) or self.typeMatches(TokenType.RPAREN):
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
                raise ParsingException("Expected table alias after keyword AS")

        return Table(table_name, schema_name, table_alias)

    def _parse_parenthesis_content(self) -> Union[SelectStatement, List[Table]]:
        """
        Parse the content inside parenthesis.

        The content can be a SELECT statement or a list of tables, with optional schema names and aliases.
        Examples:
        - (SELECT * FROM table)
        - (table1, schema_2.table2, schema_3.table3 AS table3_alias)

        Returns:
            Union[SelectStatement, List[Table]]: A SELECT statement or a list of Table objects.
        """

        super().consume(TokenType.LPAREN)

        select_parser = Parser(self.tokens)

        # TODO: This feature is not implemented yet
        select_statement = select_parser.parseSelectStatementIfMatches()

        if select_statement is not None:
            super().consume(TokenType.RPAREN)
            return select_statement
        else:
            # Case when table(s) inside parenthesis
            table_list: List[Table] = []
            table_list.append(self._parse_table())

            while self.typeMatches(TokenType.COMMA):
                super().consume(TokenType.COMMA)
                try:
                    table_list.append(self._parse_table())
                except ParsingException:
                    raise ParsingException(
                        f"Expected table name after comma, got {self.tokens[0].value} instead"
                    )

            super().consume(TokenType.RPAREN)
            return table_list
