import pytest

from baseparser import ParsingException
from sqltokenizer import Tokenizer
from tableorsubqueryparser import Table, TableOrSubqueryParser


class TestTableOrSubqueryParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_parse_table_name(self):
        tokens = self.tokenizer.tokenize("table_name")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, Table)
        assert result.table_name == "table_name"
        assert result.schema_name is None
        assert result.table_alias is None
        assert len(tokens) == 1

    def test_parse_table_name_with_schema_name(self):
        tokens = self.tokenizer.tokenize("schema_name.table_name")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, Table)
        assert result.table_name == "table_name"
        assert result.schema_name == "schema_name"
        assert result.table_alias is None
        assert len(tokens) == 1

    def test_parse_table_name_with_missing_name(self):
        tokens = self.tokenizer.tokenize("schema_name.")
        parser = TableOrSubqueryParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_parse_table_name_with_alias(self):
        tokens = self.tokenizer.tokenize("schema_name.table_name AS alias")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, Table)
        assert result.table_name == "table_name"
        assert result.schema_name == "schema_name"
        assert result.table_alias == "alias"
        assert len(tokens) == 1

    def test_parse_table_name_with_missing_alias(self):
        tokens = self.tokenizer.tokenize("schema_name.table_name AS")
        parser = TableOrSubqueryParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_parse_subquery(self):
        pass  # TODO
