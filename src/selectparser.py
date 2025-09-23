from baseparser import BaseParser, ParsingException
from qualifiedtablenameparser import QualifiedTableNameParser
from sqltoken import TokenType
from statements import SelectStatement


class SelectStatementParser(BaseParser):
    def parse(self) -> SelectStatement:
        if not self.typeMatches(TokenType.KEYWORD) and not self.valueMatches("SELECT"):
            raise ParsingException("Expected SELECT")
        self.consume(TokenType.KEYWORD, "SELECT")
        column_list = []
        if self.typeMatches(TokenType.OPERATOR) and self.valueMatches("*"):
            self.consume(TokenType.OPERATOR, "*")
        elif self.typeMatches(TokenType.IDENTIFIER):
            while not self.valueMatches("FROM"):
                column_list.append(self.consume(TokenType.IDENTIFIER).value)
                if self.typeMatches(TokenType.COMMA):
                    self.consume(TokenType.COMMA)
        else:
            raise ParsingException(f"Expected column list, got {self.tokens[0]}")

        self.consume(TokenType.KEYWORD, "FROM")

        qualified_table = QualifiedTableNameParser(self.tokens)
        qualified_table = qualified_table.parse()

        return SelectStatement(
            table_name=qualified_table.table_name,
            schema_name=qualified_table.schema_name,
            alias=qualified_table.alias,
            columns=column_list,
        )
