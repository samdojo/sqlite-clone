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

    Currently matches routes:
    - 1, 3, 4, 5, 6, 8, 11, 12, 13, 14
    of expression specification.

    NOTE:
    Routes 11/13/14/6 apply ExpressionParser recursively
    since those routes produce nested expressions.
    As such, keep in mind that in general expressions combining
    multiple expressions (such as "x AND y" or "x OR y") will
    parse sub-expressions like
    - "x AND y OR z"
    as
    - "(x AND (y OR z))"
    To specify an alternative grouping, use parentheses:
    - "((x AND y) OR z)" or equivalently "(x AND y) OR z"
    """
    def parse(self) -> Expression:
        output = Expression()
        # ROUTE 5: unary-operator
        if self.isValueOneOf(UNARIES):
            output.route = 5
            if self.valueMatches("NOT"):
                unary = self.consume(TokenType.KEYWORD).value
            else:
                unary = self.consume(TokenType.OPERATOR).value
            output.unary_op = UnaryOperator(unary)
            output.lead_expr = ExpressionParser(self.tokens).parse()
            return ExpressionParser.try_flatten(output)
        # ROUTE 8: multi-expression
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
        # ROUTE 1: literal-value
        elif LiteralParser(copy.deepcopy(self.tokens)).parseIfMatches():
            literal = LiteralParser(self.tokens).parse()
            output.lead_expr = Expression(lead_expr=literal, route=1)
        # ROUTE 3/4: column address
        elif ColumnAddressParser(copy.deepcopy(self.tokens)).parseIfMatches():
            column_address = ColumnAddressParser(self.tokens).parse()
            output.lead_expr = Expression(lead_expr=column_address, route=3)
        else:
            raise ParsingException("Unable to find parsing route for Expression")
        # ROUTE 12: ISNULL/NOTNULL/NOT NULL
        if self.isValueOneOf(["ISNULL", "NOTNULL"]) or [k.value for k in self.tokens][:2] == ["NOT", "NULL"]:
            null_str = self.consume(TokenType.KEYWORD).value
            if null_str == "NOT":
                null_str += " " + self.consume(TokenType.KEYWORD, "NULL").value
            output = Expression(
                lead_expr=Expression(
                    unary_op=null_str,
                    route=12,
                    lead_expr=output.lead_expr
                )
            )
        # ROUTE 11: NOT/LIKE part
        route_11_keys = ["LIKE", "GLOB", "REGEXP", "MATCH"]
        if self.isValueOneOf(route_11_keys) or (len(self.tokens) >1 and self.valueMatches("NOT") and self.tokens[1].value in route_11_keys):
            if self.valueMatches("NOT"):
                binary_str = self.consume(TokenType.KEYWORD, "NOT").value
                binary_str += " " + self.consume(TokenType.KEYWORD).value
            else:
                binary_str = self.consume(TokenType.KEYWORD).value
            output.binary_op = binary_str
            output.second_expr = ExpressionParser(self.tokens).parse()
            output.route = 11
            if "LIKE" in output.binary_op and self.valueMatches("ESCAPE"):
                output.ternary_op = self.consume(TokenType.KEYWORD, "ESCAPE").value
                output.third_expr = ExpressionParser(self.tokens).parse()
        # ROUTE 13: IS/NOT/DISTINCT FROM
        elif self.valueMatches("IS"):
            is_str = self.consume(TokenType.KEYWORD, "IS").value
            if self.valueMatches("NOT"):
                is_str += " " + self.consume(TokenType.KEYWORD, "NOT").value
            if self.valueMatches("DISTINCT"):
                is_str += " " + self.consume(TokenType.KEYWORD, "DISTINCT").value
                is_str += " " + self.consume(TokenType.KEYWORD, "FROM").value
            output.binary_op = is_str
            output.second_expr = ExpressionParser(self.tokens).parse()
            output.route = 13
        # ROUTE 14: BETWEEN
        elif self.valueMatches("BETWEEN") or [k.value for k in self.tokens][:2] == ["NOT", "BETWEEN"]:
            if self.valueMatches("BETWEEN"):
                between_op = self.consume(TokenType.KEYWORD, "BETWEEN").value
            else:
                between_op = self.consume(TokenType.KEYWORD, "NOT").value
                between_op += " " + self.consume(TokenType.KEYWORD, "BETWEEN").value
            output.binary_op = between_op
            output.route = 14
            and_expr = ExpressionParser(self.tokens).parse()
            if not ((and_expr.route == 6) and (and_expr.binary_op == BinaryOperator.AND)):
                raise ParsingException("BETWEEN expression missing AND operator")
            output.second_expr = and_expr.lead_expr
            output.ternary_op = "AND"
            output.third_expr = and_expr.second_expr
        # ROUTE 6: binary-operator
        elif self.isValueOneOf(BINARIES):
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
            output.binary_op = BinaryOperator(binary_str)
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
