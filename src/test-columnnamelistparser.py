import pytest

from baseparser import ParsingException
from columnnamelistparser import ColumnNameListParser
from sqltokenizer import Tokenizer


class TestColumnNameListParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_parse_column_name_list(self):
        tokens = self.tokenizer.tokenize("(column1, column2, column3)")
        parser = ColumnNameListParser(tokens)
        result = parser.parse()
        assert result == ["column1", "column2", "column3"]

    def test_parse_missing_comma(self):
        tokens = self.tokenizer.tokenize("(column1 column2 column3")
        parser = ColumnNameListParser(tokens)
        with pytest.raises(ParsingException) as e:
            parser.parse()
        assert (
            e.value.args[0]
            == "Unexpected token after column name, got Token(type=<TokenType.IDENTIFIER: 'IDENTIFIER'>, value='column2')"
        )

    def test_missing_column_name(self):
        tokens = self.tokenizer.tokenize("(column1, column2,)")
        parser = ColumnNameListParser(tokens)
        with pytest.raises(ParsingException) as e:
            parser.parse()
        assert (
            e.value.args[0]
            == "Unexpected token after comma, got Token(type=<TokenType.RPAREN: 'RPAREN'>, value=')')"
        )

    def test_missing_rparen(self):
        tokens = self.tokenizer.tokenize("(column1, column2")
        parser = ColumnNameListParser(tokens)
        with pytest.raises(ParsingException) as e:
            parser.parse()
        assert (
            e.value.args[0]
            == "Unexpected token after column name, got Token(type=<TokenType.EOF: 'EOF'>, value='')"
        )

    def test_inner_parentheses(self):
        tokens = self.tokenizer.tokenize("(column1, (column2))")
        parser = ColumnNameListParser(tokens)
        with pytest.raises(ParsingException) as e:
            parser.parse()
        assert (
            e.value.args[0]
            == "Unexpected token after comma, got Token(type=<TokenType.LPAREN: 'LPAREN'>, value='(')"
        )
