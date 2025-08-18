from parser import Parser
from typing import List, Optional, Self, TypeAlias, Union

from baseparser import BaseParser, ParsingException
from sqltoken import TokenType
from statements import SubQuery, Table

NestedTableOrSubquery: TypeAlias = List[Union[Table, SubQuery, Self]]


class TableOrSubqueryParser(BaseParser):
    """
    Parser for table or subquery.
    """

    def parse(self) -> NestedTableOrSubquery:
        """
        Recursively parses the input tokens and returns a list of tables and subqueries.

        Returns:
            List[Union[Table, SubQuery, Self]]: Nested list of tables and subqueries
        Example:
            schema.table as alias, (SELECT * FROM table2) returns \n
            [Table("table", "schema", "alias"), [SelectStatement(SELECT * FROM table2)]]
        """
        result: NestedTableOrSubquery = []
        while True:
            if self.typeMatches(TokenType.IDENTIFIER):
                result.append(self._parse_table())
            elif self.typeMatches(TokenType.LPAREN):
                super().consume(TokenType.LPAREN)
                result.append(self._parse_parenthesis_content())

            if self.typeMatches(TokenType.COMMA):
                self._handle_comma()
            elif self.typeMatches(TokenType.EOF):
                break
            else:
                raise ParsingException(f"Unexpected token {self.tokens[0]}")
        return result

    def _parse_table(self) -> Table:
        """
        Parses a table name and returns a Table object, with optional schema name and alias.

        Returns:
            Table: Table object
        Example:
            schema.table as alias returns \n
            Table("table", "schema", "alias")
        """

        first_token = super().consume(TokenType.IDENTIFIER)
        table_name = first_token.value
        schema_name = None

        if self.typeMatches(TokenType.DOT):
            super().consume(TokenType.DOT)
            schema_name = first_token.value
            if not self.typeMatches(TokenType.IDENTIFIER):
                raise ParsingException(
                    f"Unexpected token {self.tokens[0].value} after dot"
                )
            second_token = super().consume(TokenType.IDENTIFIER)
            table_name = second_token.value

        alias = self._parse_alias_if_exists(require_as=False)
        return Table(table_name, schema_name, alias)

    def _parse_parenthesis_content(self) -> NestedTableOrSubquery:
        """
        Parses the content of a parenthesis and returns a list of tables and subqueries.
        Recursively parses inner parenthese.

        Returns:
            NestedTableOrSubquery: Nested list of tables and subqueries
        Example:
            (SELECT * FROM table2) returns \n
            [SelectStatement(SELECT * FROM table2)] \n
            (table1, schema2.table2 AS alias2) returns \n'
            [Table("table1", None, None), Table("table2", "schema2", "alias2")]
        """
        result: NestedTableOrSubquery = []

        # Case for select statement
        if self.typeMatches(TokenType.KEYWORD):
            if not self.valueMatches("SELECT"):
                raise ParsingException(
                    f"Unexpected keyword {self.tokens[0].value} after '('"
                )
            select_parser = Parser(self.tokens)
            # TODO: This is not implemented yet
            select_statement = select_parser.parseSelectStatementIfMatches()
            if select_statement is not None:
                super().consume(TokenType.RPAREN)
                result.append(select_statement)
                return result

        # Case for list of tables and subqueries
        while True:
            if self.typeMatches(TokenType.RPAREN):
                raise ParsingException(f"Parenthesis cannot be empty")
            elif self.typeMatches(TokenType.LPAREN):
                super().consume(TokenType.LPAREN)
                result.append(self._parse_parenthesis_content())  # Recursive call
            elif self.typeMatches(TokenType.IDENTIFIER):
                result.append(self._parse_table())
            else:
                raise ParsingException(
                    f"Unexpected token {self.tokens[0].value} after '('"
                )

            if self.typeMatches(TokenType.COMMA):
                self._handle_comma()

            if self.typeMatches(TokenType.RPAREN):  # End of parenthesis
                break

        super().consume(TokenType.RPAREN)
        if self._parse_alias_if_exists(require_as=False):
            raise ParsingException(f"Alias not allowed for list of tables")
        return result

    def _parse_alias_if_exists(self, require_as: bool = False) -> Optional[str]:
        """
        Parses an alias if it exists.
        If require_as is True, the alias must be preceded by AS keyword.
        """
        # Implicit alias
        if self.typeMatches(TokenType.IDENTIFIER):
            if require_as:
                raise ParsingException(f"Alias requires AS keyword")
            return super().consume(TokenType.IDENTIFIER).value

        # Explicit alias using AS
        if self.typeMatches(TokenType.KEYWORD) and self.valueMatches("AS"):
            super().consume(TokenType.KEYWORD)
            if not self.typeMatches(TokenType.IDENTIFIER):
                raise ParsingException(
                    f"Unexpected token {self.tokens[0].value} after keyword AS"
                )
            return super().consume(TokenType.IDENTIFIER).value
        return None

    def _handle_comma(self) -> None:
        """
        Handles a comma in the input tokens.
        Token after comma must be identifier (a table name) or a parenthesis (a subquery)
        """
        super().consume(TokenType.COMMA)
        if not self.typeMatches(TokenType.IDENTIFIER) and not self.typeMatches(
            TokenType.LPAREN
        ):
            raise ParsingException(
                f"Unexpected token {self.tokens[0].value} after comma"
            )
