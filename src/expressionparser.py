from dataclasses import dataclass
from typing import Optional, Union
from literalparser import ColumnAddress, ColumnAddressParser, LiteralParser
from sqltoken import TokenType
from baseparser import BaseParser, ParsingException
from statements import BinaryOperator, UnaryOperator, Literal
import copy


@dataclass
class Expression:
    """Dataclass for SQLite expressions.

    Route indicates what kind of expression is contained.
    """

    route: int = -1
    expr_array: Optional[list["Expression"]] = None
    unary_op: Optional[UnaryOperator] = None
    lead_expr: Optional[Union["Expression", Literal, ColumnAddress]] = None
    binary_op: Optional[BinaryOperator] = None
    second_expr: Optional[Union["Expression", Literal, ColumnAddress]] = None


class ExpressionParser(BaseParser):
    """Parser for SQL Expressions.

    Currently matches routes 1, 3, 4, 5, 6, and 8
    of expression specification."""
    def parse(self) -> Expression:
        output = Expression()
        if self.valueIsPredicate(UnaryOperator.isUnary):
            output.route = 5
            if self.valueIsPredicate(lambda x: x == "NOT"):
                unary = self.consume(TokenType.KEYWORD).value
            else:
                unary = self.consume(TokenType.OPERATOR).value
            output.unary_op = UnaryOperator(unary)
            output.lead_expr = ExpressionParser(self.tokens).parse()
            return ExpressionParser.try_flatten(output)
        if self.valueMatches("("):
            self.consume(TokenType.LPAREN)
            next_expr = ExpressionParser(self.tokens).parse()
            expr_arr = Expression(route=8)
            expr_arr.expr_array = [next_expr]
            while not self.valueMatches(")"):
                self.consume(TokenType.COMMA)
                expr_arr.expr_array.append(ExpressionParser(self.tokens).parse())
            self.consume(TokenType.RPAREN)
            output.lead_expr = expr_arr
        elif LiteralParser(copy.deepcopy(self.tokens)).parseIfMatches():
            literal = LiteralParser(self.tokens).parse()
            output.lead_expr = Expression(lead_expr=literal, route=1)
        elif ColumnAddressParser(copy.deepcopy(self.tokens)).parseIfMatches():
            column_address = ColumnAddressParser(self.tokens).parse()
            output.lead_expr = Expression(lead_expr=column_address, route=3)
        else:
            raise ParsingException("Unable to find parsing route for Expression")
        if self.valueIsPredicate(BinaryOperator.isBinary):
            if self.typeMatches(TokenType.OPERATOR):
                binary_str = self.consume(TokenType.OPERATOR).value
            elif self.typeMatches(TokenType.COMPARISON):
                binary_str = self.consume(TokenType.COMPARISON).value
            elif self.valueIsPredicate(lambda x: x in {"AND", "OR"}):
                binary_str = self.consume(TokenType.KEYWORD).value
            else:
                raise ParsingException(
                    f"Found Binary Operator of unexpected token type: {self.tokens[0]}"
                )
            binary = BinaryOperator(binary_str)
            output.binary_op = binary
            output.second_expr = ExpressionParser(self.tokens).parse()
            output.route = 6
        else:
            output.route = output.lead_expr.route
        return ExpressionParser.try_flatten(output)

    @staticmethod
    def try_flatten(expr: Expression) -> Expression:
        """If expression contains a lead expression and no other content,
        return the lead expression. Otherwise, return the input expression.

        An expression is a "thin wrapper" over another expression if the
        top-level expression's route matches the leadd expression's route
        and if the unary, binary operators, secondary expressions, and
        expression array are all None."""
        if not isinstance(expr.lead_expr, Expression):
            return expr
        if (
            (expr.lead_expr.route == expr.route)
            and (expr.unary_op is None)
            and (expr.binary_op is None)
            and (expr.expr_array is None)
            and (expr.second_expr is None)
        ):
            return expr.lead_expr
        return expr
