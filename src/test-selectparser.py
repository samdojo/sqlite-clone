import pytest

from baseparser import ParsingException
from selectparser import SelectStatementParser
from sqltokenizer import Tokenizer


class TestSelectParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_parse_select_statement(self):
        tokens = self.tokenizer.tokenize("SELECT * FROM users")
        parser = SelectStatementParser(tokens)
        statement = parser.parse()
        assert statement.table_name == "users"
        assert statement.schema_name is None
        assert statement.alias is None
        assert statement.columns == []

    def test_parse_select_statement_with_columns(self):
        tokens = self.tokenizer.tokenize("SELECT id, name FROM users")
        parser = SelectStatementParser(tokens)
        statement = parser.parse()
        assert statement.table_name == "users"
        assert statement.schema_name is None
        assert statement.alias is None
        assert statement.columns == ["id", "name"]

    def test_parse_select_statement_with_schema(self):
        tokens = self.tokenizer.tokenize("SELECT id, name FROM main.users")
        parser = SelectStatementParser(tokens)
        statement = parser.parse()
        assert statement.table_name == "users"
        assert statement.schema_name == "main"
        assert statement.alias is None
        assert statement.columns == ["id", "name"]

    def test_parse_select_statement_with_alias(self):
        tokens = self.tokenizer.tokenize("SELECT id, name FROM users AS u")
        parser = SelectStatementParser(tokens)
        statement = parser.parse()
        assert statement.table_name == "users"
        assert statement.schema_name is None
        assert statement.alias == "u"
        assert statement.columns == ["id", "name"]

    def test_invalid_statement(self):
        tokens = self.tokenizer.tokenize("SELECT FROM users")
        parser = SelectStatementParser(tokens)
        with pytest.raises(ParsingException):
            parser.parse()
