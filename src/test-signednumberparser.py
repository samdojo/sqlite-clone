import pytest
from signednumberparser import SignedNumberParser
from sqltokenizer import Tokenizer
from baseparser import ParsingException


class TestSignedNumberParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_parse_positive_integer(self):
        tokens = self.tokenizer.tokenize('8456')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, int)
        assert result == 8456
        assert len(tokens) == 1

    def test_parse_positive_integer_with_sign(self):
        tokens = self.tokenizer.tokenize('+8153')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, int)
        assert result == 8153
        assert len(tokens) == 1

    def test_parse_negative_integer(self):
        tokens = self.tokenizer.tokenize('-8346')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, int)
        assert result == -8346
        assert len(tokens) == 1

    def test_parse_positive_float(self):
        tokens = self.tokenizer.tokenize('8.816')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, float)
        assert result == 8.816
        assert len(tokens) == 1

    def test_parse_positive_float_with_sign(self):
        tokens = self.tokenizer.tokenize('+815.3')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, float)
        assert result == 815.3
        assert len(tokens) == 1

    def test_parse_negative_float(self):
        tokens = self.tokenizer.tokenize('-885.6')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, float)
        assert result == -885.6
        assert len(tokens) == 1

    def test_parse_zero(self):
        tokens = self.tokenizer.tokenize('0')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, int)
        assert result == 0
        assert len(tokens) == 1

    def test_parse_float_zero(self):
        tokens = self.tokenizer.tokenize('0.0')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, float)
        assert result == 0.0
        assert len(tokens) == 1

    def test_parse_blank(self):
        tokens = self.tokenizer.tokenize('')
        parser = SignedNumberParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_parse_trailing_dot(self):
        tokens = self.tokenizer.tokenize('813.')
        parser = SignedNumberParser(tokens)
        result = parser.parse()
        assert isinstance(result, int)
        assert result == 813
        assert len(tokens) == 2

    def test_parse_leading_dot(self):
        tokens = self.tokenizer.tokenize('.8453')
        parser = SignedNumberParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)
