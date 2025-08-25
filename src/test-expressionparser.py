import pytest
from literalparser import ColumnAddress, Literal
from expressionparser import ExpressionParser, Expression
from sqltokenizer import Tokenizer
from baseparser import ParsingException
from statements import BinaryOperator, UnaryOperator


class TestLiteralParser:
    def setup_method(self):
        self.tokenizer = Tokenizer()

    def test_basic_expressions(self):
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
        case_2 = self.tokenizer.tokenize("test_schema.test_tbl.test_col")
        expect_2 = Expression(
            route=3,
            lead_expr=ColumnAddress("test_col", "test_tbl", "test_schema")
        )
        case_3 = self.tokenizer.tokenize("test_tbl.test_col")
        expect_3 = Expression(
            route=3,
            lead_expr=ColumnAddress("test_col", "test_tbl", )
        )
        case_4 = self.tokenizer.tokenize("test_col")
        expect_4 = Expression(
            route=3,
            lead_expr=ColumnAddress("test_col", )
        )
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
        case_6 = self.tokenizer.tokenize("NOT 1")
        expect_6 = Expression(
            route=5,
            unary_op=UnaryOperator("NOT"),
            lead_expr=Expression(
                route=1,
                lead_expr=Literal(dtype=int, value=1)
            )
        )
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
        cases = [case_1, case_2, case_3, case_4, case_5, case_6, case_7, case_8]
        expects = [expect_1, expect_2, expect_3, expect_4, expect_5, expect_6, expect_7, expect_8]
        for case, expect in zip(cases, expects):
            exprs = ExpressionParser(case).parse()
            assert exprs == expect

    def test_parenthetical(self):
        """Building up a parenthetical with binary operations."""
        true_literal = Expression(route=1, lead_expr=Literal(dtype=bool, value=True))
        false_literal = Expression(route=1, lead_expr=Literal(dtype=bool, value=False))
        case_1 = self.tokenizer.tokenize("TRUE")
        expr_1 = ExpressionParser(case_1).parse()
        expect1 = Expression(
            route=1,
            lead_expr=true_literal,
        )
        assert expr_1 == true_literal

        case_2 = self.tokenizer.tokenize("TRUE AND FALSE")
        expr_2 = ExpressionParser(case_2).parse()
        expect_2 = Expression(
            route=6,
            lead_expr=true_literal,
            binary_op=BinaryOperator("AND"),
            second_expr=false_literal,
        )
        assert expr_2 == expect_2

        case_3 = self.tokenizer.tokenize("(TRUE AND FALSE)")
        expr_3 = ExpressionParser(case_3).parse()
        expect_3 = Expression(route=8, expr_array=[expect_2])
        assert expr_3 == expect_3

        case_4 = self.tokenizer.tokenize("NOT (TRUE AND FALSE)")
        expr_4 = ExpressionParser(case_4).parse()
        expect_4 = Expression(
            route=5, unary_op=UnaryOperator("NOT"), lead_expr=expect_3
        )
        assert expr_4 == expect_4

        case_5 = self.tokenizer.tokenize("NOT (TRUE AND FALSE) OR (3 = 1+2)")
        expr_5 = ExpressionParser(case_5).parse()
        second_parentheses = Expression(
            route=8,
            expr_array=[
                Expression(
                    route=6,
                    lead_expr=Expression(
                        route=1, lead_expr=Literal(dtype=int, value=3)
                    ),
                    binary_op=BinaryOperator("="),
                    second_expr=Expression(
                        route=6,
                        lead_expr=Expression(
                            route=1, lead_expr=Literal(dtype=int, value=1)
                        ),
                        binary_op=BinaryOperator("+"),
                        second_expr=Expression(
                            route=1, lead_expr=Literal(dtype=int, value=2)
                        ),
                    ),
                )
            ],
        )
        expect_5 = Expression(
            route=5,
            unary_op=UnaryOperator("NOT"),
            lead_expr=Expression(
                route=6,
                lead_expr=expect_3,
                binary_op=BinaryOperator("OR"),
                second_expr=second_parentheses,
            ),
        )
        assert expr_5 == expect_5

    def test_failing_expressions(self):
        """Malformed expressions each on an individual route of ExpressionParser."""
        case_1 = self.tokenizer.tokenize("TRUE AND")
        case_2 = self.tokenizer.tokenize("= 5")
        case_3 = self.tokenizer.tokenize("(1 + 2")
        case_4 = self.tokenizer.tokenize("(1+ )")
        case_5 = self.tokenizer.tokenize("(1, 2, 3, 4 5, 6 )")
        case_6 = self.tokenizer.tokenize("schema..column")
        case_7 = self.tokenizer.tokenize(".table.column")
        case_8 = self.tokenizer.tokenize("schema.table.")
        case_9 = self.tokenizer.tokenize("schema.table.column.item")
        case_10 = self.tokenizer.tokenize("+")
        case_11 = self.tokenizer.tokenize("NOT")
        case_12 = self.tokenizer.tokenize("NOT (TRUE AND FALSE) OR (TRUE")
        case_13 = self.tokenizer.tokenize("3>>2")
        case_14 = self.tokenizer.tokenize("3>>>2")
        case_15 = self.tokenizer.tokenize("3><2")
        case_16 = self.tokenizer.tokenize("TRUE AND OR")
        for tokens in [
            case_1,
            case_2,
            case_3,
            case_4,
            case_5,
            case_6,
            case_7,
            case_8,
            case_9,
            case_10,
            case_11,
            case_12,
            case_13,
            case_14,
            case_15,
        ]:
            with pytest.raises(ParsingException) as p_err:
                ExpressionParser(tokens).parse()
            assert p_err.errisinstance(ParsingException)

