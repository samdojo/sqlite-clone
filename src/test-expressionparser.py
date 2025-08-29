import pytest
from expressionparser import ExpressionParser, Expression
from sqltokenizer import Tokenizer
from baseparser import ParsingException
from statements import BinaryOperator, UnaryOperator, ColumnAddress, Literal


class TestLiteralParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()
        self.int_literal = lambda x: Expression(route=1, lead_expr=Literal(dtype=int, value=x))
        self.TRUE_LITERAL = Expression(route=1, lead_expr=Literal(dtype=bool, value=True))
        self.FALSE_LITERAL = Expression(route=1, lead_expr=Literal(dtype=bool, value=False))

    def test_basic_expressions1(self):
        """Basic expressions which should all parse."""
        case_1 = self.tokenizer.tokenize("+8153")
        expect_1 = Expression(
            route=5,
            unary_op=UnaryOperator("+"),
            lead_expr=Expression(
                route=1,
                lead_expr=Literal(dtype=int, value=8153)
            )
        )
        assert expect_1 == ExpressionParser(case_1).parse()

    def test_basic_expressions2(self):
        case_2 = self.tokenizer.tokenize("test_schema.test_tbl.test_col")
        expect_2 = Expression(
            route=3,
            lead_expr=ColumnAddress("test_col", "test_tbl", "test_schema")
        )
        assert expect_2 == ExpressionParser(case_2).parse()

    def test_basic_expressions3(self):
        case_3 = self.tokenizer.tokenize("test_tbl.test_col")
        expect_3 = Expression(
            route=3,
            lead_expr=ColumnAddress("test_col", "test_tbl", )
        )
        assert expect_3 == ExpressionParser(case_3).parse()

    def test_basic_expressions4(self):
        case_4 = self.tokenizer.tokenize("test_col")
        expect_4 = Expression(
            route=3,
            lead_expr=ColumnAddress("test_col", )
        )
        assert expect_4 == ExpressionParser(case_4).parse()

    def test_basic_expressions5(self):
        case_5 = self.tokenizer.tokenize("(-150)")
        expect_5 = Expression(
            route=8,
            expr_array=[
                Expression(
                    route=5,
                    unary_op=UnaryOperator("-"),
                    lead_expr=Expression(
                        route=1,
                        lead_expr=Literal(dtype=int, value=150)
                    )
                )
            ]
        )
        assert expect_5 == ExpressionParser(case_5).parse()

    def test_basic_expressions6(self):
        case_6 = self.tokenizer.tokenize("NOT 1")
        expect_6 = Expression(
            route=5,
            unary_op=UnaryOperator("NOT"),
            lead_expr=Expression(
                route=1,
                lead_expr=Literal(dtype=int, value=1)
            )
        )
        assert expect_6 == ExpressionParser(case_6).parse()

    def test_basic_expressions7(self):
        case_7 = self.tokenizer.tokenize("(1, 0, 0, 1, 1, 0)")
        expect_7 = Expression(
            route=8,
            expr_array=[
                Expression(route=1, lead_expr=Literal(dtype=int, value=1)),
                Expression(route=1, lead_expr=Literal(dtype=int, value=0)),
                Expression(route=1, lead_expr=Literal(dtype=int, value=0)),
                Expression(route=1, lead_expr=Literal(dtype=int, value=1)),
                Expression(route=1, lead_expr=Literal(dtype=int, value=1)),
                Expression(route=1, lead_expr=Literal(dtype=int, value=0)),
            ]
        )
        assert expect_7 == ExpressionParser(case_7).parse()

    def test_basic_expressions8(self):
        case_8 = self.tokenizer.tokenize("NOT (TRUE AND FALSE)")
        expect_8 = Expression(
            route=5,
            unary_op=UnaryOperator("NOT"),
            lead_expr=Expression(
                route=8,
                expr_array=[
                    Expression(
                        route=6,
                        lead_expr=Expression(route=1, lead_expr=Literal(dtype=bool, value=True)),
                        binary_op=BinaryOperator("AND"),
                        second_expr=Expression(route=1, lead_expr=Literal(dtype=bool, value=False))
                    )
                ]
            )
        )
        assert expect_8 == ExpressionParser(case_8).parse()

    def test_parenthetical_1(self):
        """Building up a parenthetical with binary operations."""
        case_1 = self.tokenizer.tokenize("TRUE")
        expr_1 = ExpressionParser(case_1).parse()
        assert expr_1 == self.TRUE_LITERAL

    def test_parenthetical_2(self):
        case_2 = self.tokenizer.tokenize("TRUE AND FALSE")
        expr_2 = ExpressionParser(case_2).parse()
        expect_2 = Expression(
            route=6,
            lead_expr=self.TRUE_LITERAL,
            binary_op=BinaryOperator("AND"),
            second_expr=self.FALSE_LITERAL,
        )
        assert expr_2 == expect_2

    def test_parenthetical_3(self):
        case_3 = self.tokenizer.tokenize("(TRUE AND FALSE)")
        expr_3 = ExpressionParser(case_3).parse()
        expect_3 = Expression(route=8, expr_array=[Expression(
            route=6,
            lead_expr=self.TRUE_LITERAL,
            binary_op=BinaryOperator("AND"),
            second_expr=self.FALSE_LITERAL,
        )])
        assert expr_3 == expect_3

    def test_parenthetical_4(self):
        case_4 = self.tokenizer.tokenize("NOT (TRUE AND FALSE)")
        expr_4 = ExpressionParser(case_4).parse()
        expect_4 = Expression(
            route=5, unary_op=UnaryOperator("NOT"), lead_expr=Expression(route=8, expr_array=[Expression(
            route=6,
            lead_expr=self.TRUE_LITERAL,
            binary_op=BinaryOperator("AND"),
            second_expr=self.FALSE_LITERAL,
        )])
        )
        assert expr_4 == expect_4

    def test_parenthetical_5(self):
        case_5 = self.tokenizer.tokenize("NOT (TRUE AND FALSE) OR (3 = 1+2)")
        expr_5 = ExpressionParser(case_5).parse()
        second_parentheses = Expression(
            route=8,
            expr_array=[
                Expression(
                    route=6,
                    lead_expr=self.int_literal(3),
                    binary_op=BinaryOperator("="),
                    second_expr=Expression(
                        route=6,
                        lead_expr=self.int_literal(1),
                        binary_op=BinaryOperator("+"),
                        second_expr=self.int_literal(2),
                    ),
                )
            ],
        )
        expect_5 = Expression(
            route=5,
            unary_op=UnaryOperator("NOT"),
            lead_expr=Expression(
                route=6,
                lead_expr=Expression(route=8, expr_array=[Expression(
            route=6,
            lead_expr=self.TRUE_LITERAL,
            binary_op=BinaryOperator("AND"),
            second_expr=self.FALSE_LITERAL,
        )]),
                binary_op=BinaryOperator("OR"),
                second_expr=second_parentheses,
            ),
        )
        assert expr_5 == expect_5

    def test_failing_expressions_incorrect_col_addr(self):
        """Failing expressions: Incorrect column address format."""
        case_1 = self.tokenizer.tokenize("schema..column")
        case_2 = self.tokenizer.tokenize(".table.column")
        case_3 = self.tokenizer.tokenize("schema.table.")
        case_4 = self.tokenizer.tokenize("schema.table.column.item")
        case_5 = self.tokenizer.tokenize("..column")
        for tokens in [
            case_1,
            case_2,
            case_3,
            case_4,
            case_5,
        ]:
            with pytest.raises(ParsingException) as p_err:
                ExpressionParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)

    def test_failing_expressions_unrecognized_bin_ops(self):
        """Unrecognized binary operators."""
        case_1 = self.tokenizer.tokenize("3>>2")
        case_2 = self.tokenizer.tokenize("3>>>2")
        case_3 = self.tokenizer.tokenize("3><2")
        for tokens in [
            case_1,
            case_2,
            case_3,
        ]:
            with pytest.raises(ParsingException) as p_err:
                ExpressionParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)

    def test_failing_expressions_missing_operands(self):
        """Binary or Unary operation expressions missing operands."""
        case_1 = self.tokenizer.tokenize("TRUE AND")
        case_2 = self.tokenizer.tokenize("AND FALSE")
        case_3 = self.tokenizer.tokenize("= 5")
        case_4 = self.tokenizer.tokenize("(1+ )")
        case_5 = self.tokenizer.tokenize("+")
        case_6 = self.tokenizer.tokenize("NOT")
        for tokens in [
            case_1,
            case_2,
            case_3,
            case_4,
            case_5,
            case_6,
        ]:
            with pytest.raises(ParsingException) as p_err:
                ExpressionParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)

    def test_failing_expressions_missing_parentheses(self):
        """Expression has improper bracketing"""
        case_1 = self.tokenizer.tokenize("(1 + 2")
        case_2 = self.tokenizer.tokenize("NOT (TRUE AND FALSE) OR (TRUE")
        for tokens in [
            case_1,
            case_2,
        ]:
            with pytest.raises(ParsingException) as p_err:
                ExpressionParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)

    def test_other_failing_expressions(self):
        """Other malformed expressions."""
        # Missing comma
        case_1 = self.tokenizer.tokenize("(1, 2, 3, 4 5, 6 )")
        # 2nd operand is an operator, not an expression
        case_2 = self.tokenizer.tokenize("TRUE AND OR")
        for tokens in [
            case_1,
            case_2,
        ]:
            with pytest.raises(ParsingException) as p_err:
                ExpressionParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)
