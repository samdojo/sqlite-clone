import pytest

from baseparser import ParsingException
from createtableparser import CreateTableParser
from sqltokenizer import Tokenizer
from statements import Column


class TestCreateTableParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_parse_table(self):
        tokens = self.tokenizer.tokenize("CREATE TABLE test (id INT, name VARCHAR)")
        parser = CreateTableParser(tokens)
        result = parser.parse()
        assert result.table_name == "test"
        print(result.columns)
        assert result.columns == [
            Column(
                name="id",
                type="INT",
                nullable=True,
                default=None,
                primary_key=False,
                unique=False,
                constraints=[],
            ),
            Column(
                name="name",
                type="VARCHAR",
                nullable=True,
                default=None,
                primary_key=False,
                unique=False,
                constraints=[],
            ),
        ]

    def test_parse_table_with_schema_name(self):
        tokens = self.tokenizer.tokenize(
            "CREATE TABLE schema_name.test (id INT, name VARCHAR)"
        )
        parser = CreateTableParser(tokens)
        result = parser.parse()
        assert result.schema_name == "schema_name"
        assert result.table_name == "test"
        assert result.columns == [
            Column(
                name="id",
                type="INT",
                nullable=True,
                default=None,
                primary_key=False,
                unique=False,
                constraints=[],
            ),
            Column(
                name="name",
                type="VARCHAR",
                nullable=True,
                default=None,
                primary_key=False,
                unique=False,
                constraints=[],
            ),
        ]

    def test_invalid_statement(self):
        tokens = self.tokenizer.tokenize("CREATE table_name (id INT, name VARCHAR)")
        parser = CreateTableParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_missing_table_name(self):
        tokens = self.tokenizer.tokenize("CREATE TABLE (id INT, name VARCHAR)")
        parser = CreateTableParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_missing_parenthesis(self):
        tokens = self.tokenizer.tokenize("CREATE TABLE test id INT, name VARCHAR)")
        parser = CreateTableParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_parse_table_with_primary_key(self):
        tokens = self.tokenizer.tokenize("CREATE TABLE test (id INT PRIMARY KEY )")
        parser = CreateTableParser(tokens)
        result = parser.parse()
        assert result.table_name == "test"
        assert result.columns == [
            Column(
                name="id",
                type="INT",
                nullable=False,
                default=None,
                primary_key=True,
                unique=False,
                constraints=[],
            )
        ]

    def test_parse_table_with_parenthesis_type(self):
        tokens = self.tokenizer.tokenize(
            "CREATE TABLE test (id INT, name VARCHAR(255))"
        )
        parser = CreateTableParser(tokens)
        result = parser.parse()
        assert result.table_name == "test"
        assert result.columns == [
            Column(
                name="id",
                type="INT",
                nullable=True,
                default=None,
                primary_key=False,
                unique=False,
                constraints=[],
            ),
            Column(
                name="name",
                type="VARCHAR(255)",
                nullable=True,
                default=None,
                primary_key=False,
                unique=False,
                constraints=[],
            ),
        ]
