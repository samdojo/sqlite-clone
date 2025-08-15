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
        assert isinstance(result, list)
        assert result[0].table_name == "table_name"
        assert result[0].schema_name is None
        assert result[0].alias is None
        assert len(tokens) == 1

    def test_parse_table_name_with_schema_name(self):
        tokens = self.tokenizer.tokenize("schema_name.table_name")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert result[0].table_name == "table_name"
        assert result[0].schema_name == "schema_name"
        assert result[0].alias is None
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
        assert isinstance(result, list)
        assert result[0].table_name == "table_name"
        assert result[0].schema_name == "schema_name"
        assert result[0].alias == "alias"
        assert len(tokens) == 1

    def test_parse_table_name_with_implicit_alias(self):
        tokens = self.tokenizer.tokenize("schema_name.table_name alias")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert result[0].table_name == "table_name"
        assert result[0].schema_name == "schema_name"
        assert result[0].alias == "alias"
        assert len(tokens) == 1

    def test_comma_seperated_table_list(self):
        tokens = self.tokenizer.tokenize("table1, table2")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert result[0] == Table("table1", None, None)
        assert result[1] == Table("table2", None, None)
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
        assert result[0][0] == Table("table1", None, None)
        assert len(tokens) == 1

    def test_parse_table_list_with_schema_in_parenthesis(self):
        tokens = self.tokenizer.tokenize("(schema_name.table1)")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert result[0][0] == Table("table1", "schema_name", None)
        assert len(tokens) == 1

    def test_parse_table_list_with_schema_and_alias_in_parenthesis(self):
        tokens = self.tokenizer.tokenize("(schema_name.table1 AS table1_alias)")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert result[0][0] == Table("table1", "schema_name", "table1_alias")
        assert len(tokens) == 1

    def test_parse_table_list_in_parenthesis(self):
        tokens = self.tokenizer.tokenize(
            "(table1, schema2.table2, schema3.table3 AS table3_alias, schema4.table4 table4_alias)"
        )
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        items = result[0]
        assert len(items) == 4
        assert items[0] == Table("table1", None, None)
        assert items[1] == Table("table2", "schema2", None)
        assert items[2] == Table("table3", "schema3", "table3_alias")
        assert items[3] == Table("table4", "schema4", "table4_alias")
        assert len(tokens) == 1

    def test_parse_table_list_mixed_with_parenthesis(self):
        tokens = self.tokenizer.tokenize(
            "table1, (schema2.table2, schema3.table3 AS table3_alias), schema4.table4 table4_alias"
        )
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert result[0] == Table("table1", None, None)
        assert result[1][0] == Table("table2", "schema2", None)
        assert result[1][1] == Table("table3", "schema3", "table3_alias")
        assert result[2] == Table("table4", "schema4", "table4_alias")
        assert len(tokens) == 1

    def test_alias_outside_parenthesis(self):
        tokens = self.tokenizer.tokenize("(table1) AS t1_alias")
        parser = TableOrSubqueryParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_nested_parenthesis(self):
        tokens = self.tokenizer.tokenize("((table1))")
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert isinstance(result, list)
        assert result[0][0][0] == Table("table1", None, None)
        assert len(result[0]) == 1
        assert len(tokens) == 1

    def test_nested_parenthesis_extended(self):
        tokens = self.tokenizer.tokenize(
            "(table1, (table2), ((table3 AS table3_alias)))"
        )
        parser = TableOrSubqueryParser(tokens)
        result = parser.parse()
        assert len(result) == 1
        assert isinstance(result, list)
        items = result[0]
        assert len(items) == 3
        assert items[0] == Table("table1", None, None)
        assert items[1][0] == Table("table2", None, None)
        assert items[2][0][0] == Table("table3", None, "table3_alias")
        assert len(tokens) == 1

    def test_parse_table_list_with_missing_table_name(self):
        tokens = self.tokenizer.tokenize("(table1,)")
        parser = TableOrSubqueryParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_parse_subquery(self):
        pass  # TODO

    def test_parse_empty_parenthesis(self):
        tokens = self.tokenizer.tokenize("()")
        parser = TableOrSubqueryParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)
