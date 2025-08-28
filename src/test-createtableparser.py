from createtableparser import CreateTableParser
from sqltokenizer import Tokenizer
from statements import Column


class TestCreateTableParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_parse_table(self):
        tokens = self.tokenizer.tokenize(
            "CREATE TABLE test (id INT, name VARCHAR(255))"
        )
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
                constraints=[",", "NAME", "VARCHAR", "(", "255", ")", ")", ""],
            )
        ]
