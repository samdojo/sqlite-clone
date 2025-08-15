import pytest
from literalparser import BlobLiteralParser, BoolNullParser, LiteralParser
from sqltokenizer import Tokenizer
from baseparser import ParsingException


class TestLiteralParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_parse_positive_integer_with_sign(self):
        tokens = self.tokenizer.tokenize('+8153')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert isinstance(result, int)
        assert result == 8153
        assert len(tokens) == 1

    def test_parse_negative_integer(self):
        tokens = self.tokenizer.tokenize('-8346')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert isinstance(result, int)
        assert result == -8346
        assert len(tokens) == 1

    def test_parse_positive_float(self):
        tokens = self.tokenizer.tokenize('8.816')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert isinstance(result, float)
        assert result == 8.816
        assert len(tokens) == 1

    def test_parse_positive_float_with_sign(self):
        tokens = self.tokenizer.tokenize('+815.3')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert isinstance(result, float)
        assert result == 815.3
        assert len(tokens) == 1

    def test_parse_negative_float(self):
        tokens = self.tokenizer.tokenize('-885.6')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert isinstance(result, float)
        assert result == -885.6
        assert len(tokens) == 1

    def test_parse_trailing_dot(self):
        tokens = self.tokenizer.tokenize('813.')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert isinstance(result, int)
        assert result == 813
        assert len(tokens) == 2

    def test_parse_leading_dot(self):
        tokens = self.tokenizer.tokenize('.8453')
        parser = LiteralParser(tokens)
        with pytest.raises(ParsingException) as error:
            parser.parse()
        assert error.errisinstance(ParsingException)

    def test_parse_true(self):
        tokens = self.tokenizer.tokenize('TRUE')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert result is True

    def test_parse_false(self):
        tokens = self.tokenizer.tokenize('FALSE')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert result is False

    def test_parse_null(self):
        tokens = self.tokenizer.tokenize('NULL')
        parser = LiteralParser(tokens)
        result = parser.parse().value
        assert result is None

    def test_parse_not_bool_null(self):
        tokens = self.tokenizer.tokenize("true false null NONE")
        parsers = [BoolNullParser([token]) for token in tokens]
        for parser in parsers:
            with pytest.raises(ParsingException, match=r"expected TRUE/FALSE/NULL") as p_err:
                parser.parse()
            assert p_err.errisinstance(ParsingException)

    def test_parse_binaries(self):
        test_inputs_outputs = [
            (f"x'{'test_str'.encode().hex()}'", 'test_str'.encode()),
            (f"X'{'Hello World!'.encode().hex()}'", 'Hello World!'.encode()),
            (f'x"{"()()()".encode().hex()}"', '()()()'.encode()),
            (f'X"{"10".encode().hex()}"', '10'.encode()),
        ]
        for input, expected in test_inputs_outputs:
            tokens = self.tokenizer.tokenize(input)
            bin_parser = BlobLiteralParser(tokens)
            result = bin_parser.parse()
            assert result == expected

    def test_parse_incorrect_binaries(self):
        data = 'some data'.encode().hex()
        bad_samples = [f"'{data}'", f"{data}", f"Y'{data}'",]
        for sample in bad_samples:
            tokens = self.tokenizer.tokenize(sample)
            with pytest.raises(ParsingException, match=r"without leading x or X") as p_err:
                BlobLiteralParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)


    def test_parse_binaries_incorrect_quotes(self):
        data = 'some data'.encode().hex()
        bad_samples = [
                f'x"{data}',
                f'x{data}"',
                f'''x'{data}"''',
                f"""x"{data}'""",
                f'x`{data}`',
        ]
        for sample in bad_samples:
            print(sample)
            tokens = self.tokenizer.tokenize(sample)
            print(tokens)
            with pytest.raises(ParsingException, match=r"needs matching quotes around data") as p_err:
                BlobLiteralParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)


    def test_parse_successful_strings(self):
        tokens_1 = self.tokenizer.tokenize('"some string"')
        parser_1 = LiteralParser(tokens_1)
        result_1 = parser_1.parse().value
        assert result_1 == 'some string'

        tokens_2 = self.tokenizer.tokenize("'TRUE'")
        parser_2 = LiteralParser(tokens_2)
        result_2 = parser_2.parse().value
        assert result_2 == 'TRUE'

        tokens_3 = self.tokenizer.tokenize('"UPDATE"')
        parser_3 = LiteralParser(tokens_3)
        result_3 = parser_3.parse().value
        assert result_3 == "UPDATE"

    def test_parse_unsuccessful_strings(self):
        tokens_1 = self.tokenizer.tokenize('some string')
        with pytest.raises(ParsingException) as p_err:
            LiteralParser(tokens_1).parse()
        assert p_err.errisinstance(ParsingException)

        tokens_2 = self.tokenizer.tokenize('UPDATE')
        with pytest.raises(ParsingException) as p_err:
            LiteralParser(tokens_2).parse()
        assert p_err.errisinstance(ParsingException)
