from typing import Optional
from literalparser import LiteralParser
from sqltoken import TokenType
from baseparser import BaseParser, ParsingException
from statements import BinaryOperator, ColumnAddress, UnaryOperator, Expression
import copy

UNARIES = [k.value for k in UnaryOperator]
BINARIES = [k.value for k in BinaryOperator]


class ColumnAddressParser(BaseParser):
    """Parser for (qualified) column names."""
    def parse(self) -> ColumnAddress:
        identifiers = []
        identifiers.append(self.consume(TokenType.IDENTIFIER).value)
        if not self.typeMatches(TokenType.DOT):
            return ColumnAddress(column_name=identifiers[0])
        self.consume(TokenType.DOT)
        identifiers.append(self.consume(TokenType.IDENTIFIER).value)
        if not self.typeMatches(TokenType.DOT):
            return ColumnAddress(column_name=identifiers[1], table_name=identifiers[0])
        self.consume(TokenType.DOT)
        identifiers.append(self.consume(TokenType.IDENTIFIER).value)
        return ColumnAddress(
            column_name=identifiers[2],
            table_name=identifiers[1],
            schema_name=identifiers[0]
        )

    def parseIfMatches(self) -> Optional[ColumnAddress]:
        try:
            return self.parse()
        except ParsingException:
            return None


class ExpressionParser(BaseParser):
    """Parser for SQL Expressions.

    Currently matches routes 1, 3, 4, 5, 6, and 8
    of expression specification."""
    def parse(self) -> Expression:
        output = Expression()
        if self.isValueOneOf(UNARIES):
            output.route = 5
            if self.valueMatches("NOT"):
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
        if self.isValueOneOf(BINARIES):
            if self.typeMatches(TokenType.OPERATOR):
                binary_str = self.consume(TokenType.OPERATOR).value
            elif self.typeMatches(TokenType.COMPARISON):
                binary_str = self.consume(TokenType.COMPARISON).value
            elif self.isValueOneOf(["AND", "OR"]):
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
