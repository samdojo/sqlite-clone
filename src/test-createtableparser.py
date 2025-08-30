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

    def test_parse_table_with_constraints(self):
        tokens = self.tokenizer.tokenize("CREATE TABLE test (id INT PRIMARY KEY)")
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

    def test_parse_table_with_constraints_parenthesis(self):  # Currently not supported
        tokens = self.tokenizer.tokenize("CREATE TABLE test (name VARCHAR(255))")
        parser = CreateTableParser(tokens)
        result = parser.parse()
        assert result.table_name == "test"
        assert result.columns == [
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
