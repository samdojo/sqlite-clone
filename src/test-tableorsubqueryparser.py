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

    def test_parse_table_in_parenthesis(self):
        tokens = self.tokenizer.tokenize("(table1)")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == Table("table1", None, None)
        assert len(tokens) == 1

    def test_parse_table_list_with_schema_in_parenthesis(self):
        tokens = self.tokenizer.tokenize("(schema_name.table1)")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == Table("table1", "schema_name", None)
        assert len(tokens) == 1

    def test_parse_table_list_with_schema_and_alias_in_parenthesis(self):
        tokens = self.tokenizer.tokenize("(schema_name.table1 AS table1_alias)")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == Table("table1", "schema_name", "table1_alias")
        assert len(tokens) == 1

    def test_parse_table_list(self):
        tokens = self.tokenizer.tokenize(
            "(table1, schema2.table2, schema3.table3 AS table3_alias)"
        )
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == Table("table1", None, None)
        assert result[1] == Table("table2", "schema2", None)
        assert result[2] == Table("table3", "schema3", "table3_alias")
        assert len(tokens) == 1

    def test_parse_table_list_with_missing_table_name(self):
        tokens = self.tokenizer.tokenize("(table1,)")
        parser = TableOrSubqueryParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_parse_subquery(self):
        pass  # TODO

    def test_parse_missing_subquery(self):
        tokens = self.tokenizer.tokenize("()")
        parser = TableOrSubqueryParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)
