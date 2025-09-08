import pytest
from sqltokenizer import Tokenizer
from baseparser import ParsingException
from typenameparser import TypeNameParser
from statements import TypeAffinities, TypeName


class TestSignedNumberParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    # INT parses
    def test_type_int_1(self):
        name = "FLOATING_POINT PRIMARY KEY"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName("FLOATING_POINT", (None, None), TypeAffinities.INTEGER)
        assert result == expect

    def test_type_int_2(self):
        name = "INT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.INTEGER)
        assert result == expect

    def test_type_int_3(self):
        name = "INTEGER"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.INTEGER)
        assert result == expect

    def test_type_int_4(self):
        name = "INTEGER_VALUE"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.INTEGER)
        assert result == expect

    def test_type_int_5(self):
        name = "INT_AAAAA"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.INTEGER)
        assert result == expect

    def test_type_int_6(self):
        name = "BIGINT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.INTEGER)
        assert result == expect

    # TEXT parses
    def test_type_text_1(self):
        name = "TEXT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.TEXT)
        assert result == expect

    def test_type_text_2(self):
        name = "STR_TEXT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.TEXT)
        assert result == expect

    def test_type_text_3(self):
        name = "VARCHAR"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.TEXT)
        assert result == expect

    def test_type_text_4(self):
        name = "VARYING_CHARACTER"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.TEXT)
        assert result == expect

    def test_type_text_5(self):
        name = "CLOB"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.TEXT)
        assert result == expect

    # BLOB parses
    def test_type_blob_1(self):
        name = "BLOB NOT NULL"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName("BLOB", (None, None), TypeAffinities.BLOB)
        assert result == expect

    def test_type_blob_2(self):
        name = "BLOB_DATA"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.BLOB)
        assert result == expect

    # REAL parses
    def test_type_real_1(self):
        name = "REAL"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.REAL)
        assert result == expect

    def test_type_real_2(self):
        name = "DOUBLE"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.REAL)
        assert result == expect

    def test_type_real_3(self):
        name = "DOUBLE_PRECISION"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.REAL)
        assert result == expect

    def test_type_real_4(self):
        name = "DOUBLEPRECISION"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.REAL)
        assert result == expect

    def test_type_real_5(self):
        name = "FLOAT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.REAL)
        assert result == expect

    def test_type_real_6(self):
        name = "FLOATING_PNT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.REAL)
        assert result == expect

    # NUMERIC parses
    def test_type_numeric_1(self):
        name = "STRING"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.NUMERIC)
        assert result == expect

    def test_type_numeric_2(self):
        name = "BOOL"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.NUMERIC)
        assert result == expect

    def test_type_numeric_3(self):
        name = "BOOLEAN"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.NUMERIC)
        assert result == expect

    def test_type_numeric_4(self):
        name = "DATE"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.NUMERIC)
        assert result == expect

    def test_type_numeric_5(self):
        name = "DATETIME"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.NUMERIC)
        assert result == expect

    # Order of precedence test
    def test_parse_order_1(self):
        name = "INT_TEXT_BLOB_FLOAT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.INTEGER)
        assert result == expect

    def test_parse_order_2(self):
        name = "BLOB_CHAR_FLOAT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.TEXT)
        assert result == expect

    def test_parse_order_3(self):
        name = "BLOB_FLOAT"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.BLOB)
        assert result == expect

    def test_parse_order_4(self):
        name = "FLOAT_NUMERIC"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName(name, (None, None), TypeAffinities.REAL)
        assert result == expect

    # numeric arg parse
    def test_numeric_args_1(self):
        name = "VARCHAR(255)"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName("VARCHAR", (255, None), TypeAffinities.TEXT)
        assert result == expect

    def test_numeric_args_2(self):
        name = "DECIMAL (10,5)"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName("DECIMAL", (10, 5), TypeAffinities.NUMERIC)
        assert result == expect

    def test_numeric_args_3(self):
        name = "NCHAR(55)"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName("NCHAR", (55, None), TypeAffinities.TEXT)
        assert result == expect

    def test_numeric_args_4(self):
        name = "BOOLEAN (55)"
        tokens = self.tokenizer.tokenize(name)
        result = TypeNameParser(tokens).parse()
        expect = TypeName("BOOLEAN", (55, None), TypeAffinities.NUMERIC)
        assert result == expect

    # Failing cases
    def test_wrong_token_type_1(self):
        name = "(INT)"
        tokens = self.tokenizer.tokenize(name)
        with pytest.raises(ParsingException) as e:
            TypeNameParser(tokens).parse()
        assert e.errisinstance(ParsingException)

    def test_wrong_token_type_2(self):
        name = "+INT"
        tokens = self.tokenizer.tokenize(name)
        with pytest.raises(ParsingException) as e:
            TypeNameParser(tokens).parse()
        assert e.errisinstance(ParsingException)

    def test_wrong_token_type_3(self):
        name = ",BLOB"
        tokens = self.tokenizer.tokenize(name)
        with pytest.raises(ParsingException) as e:
            TypeNameParser(tokens).parse()
        assert e.errisinstance(ParsingException)

    def test_incomplete_num_args_1(self):
        name = "BLOB(10,5 PRIMARY KEY"
        tokens = self.tokenizer.tokenize(name)
        with pytest.raises(ParsingException) as e:
            TypeNameParser(tokens).parse()
        assert e.errisinstance(ParsingException)

    def test_incomplete_num_args_2(self):
        name = "BLOB(10 5)"
        tokens = self.tokenizer.tokenize(name)
        with pytest.raises(ParsingException) as e:
            TypeNameParser(tokens).parse()
        assert e.errisinstance(ParsingException)

    def test_incomplete_num_args_3(self):
        name = "BLOB (10, 5 NOT NULL"
        tokens = self.tokenizer.tokenize(name)
        with pytest.raises(ParsingException) as e:
            TypeNameParser(tokens).parse()
        assert e.errisinstance(ParsingException)
