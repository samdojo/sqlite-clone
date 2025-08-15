from parser import Parser
from typing import List, Optional, Union

from baseparser import BaseParser, ParsingException
from sqltoken import TokenType
from statements import SubQuery, Table


class TableOrSubqueryParser(BaseParser):
    """
    Parser for table or subquery.
    """

    def parse(self) -> List[Union[Table, SubQuery, List[Union[Table, SubQuery]]]]:
        """
        Recursively parses the input tokens and returns a list of tables and subqueries.

        Returns:
            List[Union[Table, SubQuery]]: List of tables and subqueries
        Example:
            schema.table as alias, (SELECT * FROM table2) as alias2 returns \n
            [Table("table", "schema", "alias"), SubQuery(SelectStatement(SELECT * FROM table2), "alias2")]
        """
        result: List[Union[Table, SubQuery]] = []
        while True:
            if self.typeMatches(TokenType.IDENTIFIER):
                result.append(self._parse_table())
            elif self.typeMatches(TokenType.LPAREN):
                super().consume(TokenType.LPAREN)
                result.append(self._parse_parenthesis_content())
            elif self.typeMatches(TokenType.COMMA):
                self._handle_comma()
            else:
                break
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

    def _parse_parenthesis_content(self) -> List[Union[Table, SubQuery]]:
        """
        Parses the content of a parenthesis and returns a list of tables and subqueries.
        Recursively parses inner parenthese.

        Returns:
            List[Union[Table, SubQuery]]: List of tables and subqueries
        Example:
            (SELECT * FROM table2) AS alias returns \n
            [SubQuery(SelectStatement(SELECT * FROM table2), "alias")] \n
            (table1, schema2.table2 AS alias2) returns \n
            [Table("table1", None, None), Table("table2", "schema2", "alias2")]
        """
        result: List[Union[Table, SubQuery]] = []

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
                alias = self._parse_alias_if_exists(require_as=True)
                result.append(SubQuery(select_statement, alias))
                return result

        # Case for list of tables and subqueries
        while True:
            if self.typeMatches(TokenType.RPAREN):
                raise ParsingException(f"Parenthesis cannot be empty")
            elif self.typeMatches(TokenType.LPAREN):
                super().consume(TokenType.LPAREN)
                result.append(self._parse_parenthesis_content())
            elif self.typeMatches(TokenType.IDENTIFIER):
                result.append(self._parse_table())
            else:
                raise ParsingException(
                    f"Unexpected token {self.tokens[0].value} after '('"
                )

            if self.typeMatches(TokenType.COMMA):  # Comma inside parenthesis
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

    def _handle_comma(self):
        """
        Handles a comma in the input tokens.
        """
        super().consume(TokenType.COMMA)
        # Token after comma must be a table name or a parenthesis
        if not self.typeMatches(TokenType.LPAREN) and not self.typeMatches(
            TokenType.IDENTIFIER
        ):
            raise ParsingException(
                f"Unexpected token {self.tokens[0].value} after comma"
            )
