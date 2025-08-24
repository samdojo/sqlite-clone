import pytest
from sqltokenizer import Tokenizer
from baseparser import ParsingException
from statements import Table
from qualifiedtablenameparser import QualifiedTableNameParser


class TestQualifiedTableNameParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    # Good Cases

    def test_table_only(self):
        tokens = self.tokenizer.tokenize("SomeTable")
        parser = QualifiedTableNameParser(tokens)
        result = parser.parse()
        assert result == Table("SomeTable", None, None)

    def test_schema_dot_table(self):
        tokens = self.tokenizer.tokenize("SomeSchema.SomeTable")
        parser = QualifiedTableNameParser(tokens)
        result = parser.parse()
        assert result == Table("SomeTable", "SomeSchema", None)

    def test_table_as_alias(self):
        tokens = self.tokenizer.tokenize("SomeTable AS t")
        parser = QualifiedTableNameParser(tokens)
        result = parser.parse()
        assert result == Table("SomeTable", None, "t")

    def test_table_implicit_alias(self):
        tokens = self.tokenizer.tokenize("SomeTable t")
        parser = QualifiedTableNameParser(tokens)
        result = parser.parse()
        assert result == Table("SomeTable", None, "t")

    def test_schema_table_with_alias(self):
        tokens = self.tokenizer.tokenize("SomeSchema.SomeTable AS t")
        parser = QualifiedTableNameParser(tokens)
        result = parser.parse()
        assert result == Table("SomeTable", "SomeSchema", "t")

    # Bad Cases

    def test_error_missing_table_after_dot(self):
        tokens = self.tokenizer.tokenize("SomeSchema.")
        parser = QualifiedTableNameParser(tokens)
        with pytest.raises(ParsingException):
            parser.parse()

    def test_error_as_without_alias(self):
        tokens = self.tokenizer.tokenize("SomeTable AS")
        parser = QualifiedTableNameParser(tokens)
        with pytest.raises(ParsingException):
            parser.parse()

    def test_error_starts_with_non_identifier(self):
        tokens = self.tokenizer.tokenize("UPDATE")
        parser = QualifiedTableNameParser(tokens)
        with pytest.raises(ParsingException):
            parser.parse()
