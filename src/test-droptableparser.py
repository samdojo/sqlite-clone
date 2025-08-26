import pytest
from droptableparser import DropTableParser
from statements import DropTableStatement
from sqltoken import Token, TokenType
from baseparser import ParsingException


def make_tokens(values_types):
    """Helper: convert (value, type) pairs into Token objects."""
    return [Token(value=v, type=t) for v, t in values_types]


class TestDropTableParser:

    def test_simple_drop_table(self):
        tokens = make_tokens([
            ("DROP", TokenType.KEYWORD),
            ("TABLE", TokenType.KEYWORD),
            ("users", TokenType.IDENTIFIER),
        ])
        parser = DropTableParser(tokens)
        stmt = parser.parse()
        assert isinstance(stmt, DropTableStatement)
        assert stmt.table_name == "users"
        assert stmt.schema_name is None
        assert stmt.if_exists is False

    def test_drop_table_if_exists(self):
        tokens = make_tokens([
            ("DROP", TokenType.KEYWORD),
            ("TABLE", TokenType.KEYWORD),
            ("IF", TokenType.KEYWORD),
            ("EXISTS", TokenType.KEYWORD),
            ("users", TokenType.IDENTIFIER),
        ])
        parser = DropTableParser(tokens)
        stmt = parser.parse()
        assert stmt.if_exists is True
        assert stmt.table_name == "users"
        assert stmt.schema_name is None

    def test_drop_table_with_schema(self):
        tokens = make_tokens([
            ("DROP", TokenType.KEYWORD),
            ("TABLE", TokenType.KEYWORD),
            ("public", TokenType.IDENTIFIER),
            (".", TokenType.DOT),
            ("orders", TokenType.IDENTIFIER),
        ])
        parser = DropTableParser(tokens)
        stmt = parser.parse()
        assert stmt.schema_name == "public"
        assert stmt.table_name == "orders"
        assert stmt.if_exists is False

    def test_missing_drop_keyword_raises(self):
        tokens = make_tokens([
            ("TABLE", TokenType.KEYWORD),
            ("users", TokenType.IDENTIFIER),
        ])
        parser = DropTableParser(tokens)
        with pytest.raises(ParsingException) as e:
            parser.parse()
        assert str(e.value) == "Expected DROP"

    def test_missing_table_keyword_raises(self):
        tokens = make_tokens([
            ("DROP", TokenType.KEYWORD),
            ("users", TokenType.IDENTIFIER),
        ])
        parser = DropTableParser(tokens)
        with pytest.raises(ParsingException) as e:
            parser.parse()
        assert str(e.value) == "Expected TABLE"

    def test_malformed_schema_raises(self):
        tokens = make_tokens([
            ("DROP", TokenType.KEYWORD),
            ("TABLE", TokenType.KEYWORD),
            (".", TokenType.DOT),
            ("users", TokenType.IDENTIFIER),
        ])
        parser = DropTableParser(tokens)
        with pytest.raises(ParsingException):
            parser.parse()

    def test_extra_tokens_after_statement(self):
        tokens = make_tokens([
            ("DROP", TokenType.KEYWORD),
            ("TABLE", TokenType.KEYWORD),
            ("users", TokenType.IDENTIFIER),
            ("extra", TokenType.IDENTIFIER),
        ])
        parser = DropTableParser(tokens)
        stmt = parser.parse()
        assert stmt.table_name == "users"
        # Extra token should remain in parser.tokens
        assert parser.tokens  # not empty
