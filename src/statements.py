import typing
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeAlias, Union


@dataclass
class Column:
    name: str
    type: Type | None = None
    nullable: bool = True
    default: Optional[Any] = None
    primary_key: bool = False
    unique: bool = False
    constraints: list[str] = field(default_factory=list)


@dataclass
class UpdateStatement:
    table: Any  # QualifiedTableName
    set_assignments: List[
        Dict[str, Any]
    ]  # [{'columns': [...], 'expression': ..., 'is_column_list': bool}]
    from_clause: Optional[Any] = None  # TableOrSubQuery
    where_expr: Optional[Any] = None  # Expression
    returning_exprs: Optional[List[Any]] = None  # List[Expression]
    or_action: Optional[str] = None  # "ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"


@dataclass
class CreateTableStatement:
    table_name: str
    schema_name: Optional[str]  # TODO: add support to parser
    columns: List[Column]


@dataclass
class DropTableStatement:
    table_name: str
    schema_name: Optional[str] = None
    if_exists: bool = False


@dataclass
class SelectStatement:
    schema_name: Optional[str]
    table_name: str
    alias: Optional[str]
    columns: Optional[List[str]]


LiteralType: TypeAlias = int | float | bool | str | bytes | None


class TypeAffinities(str, Enum):
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    BLOB = "BLOB"
    REAL = "REAL"
    NUMERIC = "NUMERIC"


@dataclass
class TypeName:
    name: str
    numeric_args: (
        tuple[None, None] | tuple[str | float, None] | tuple[str | float, str | float]
    )
    type_affinity: TypeAffinities


@dataclass
class Literal:
    """Container for constant value."""

    dtype: type
    value: LiteralType


@dataclass
class QualifiedTableName:
    """Container for table name, schema name and alias."""

    table_name: str
    schema_name: Optional[str]
    alias: Optional[str]


SubQuery: TypeAlias = SelectStatement


class UnaryOperator(str, Enum):
    BITWISE_NOT = "~"
    POSITIVE = "+"
    NEGATIVE = "-"
    NOT = "NOT"


class BinaryOperator(str, Enum):
    STRING_CONCAT = "||"
    MULT = "*"
    DIVIDE = "/"
    MOD = "%"
    PLUS = "+"
    MINUS = "-"
    AMPERSAND = "&"
    BAR = "|"
    LESS = "<"
    GREATER = ">"
    LESS_EQ = "<="
    GREATER_EQ = ">="
    EQLS = "="
    DBL_EQLS = "=="
    DIAMOND = "<>"
    NOT_EQLS = "!="
    AND = "AND"
    OR = "OR"


@dataclass
class ColumnAddress:
    """Dataclass for column address including optional table and schema."""

    column_name: str
    table_name: Optional[str] = None
    schema_name: Optional[str] = None


BinaryLiterals = typing.Literal[
    "ISNULL",
    "NOTNULL",
    "NOT NULL",
    "IS",
    "IS NOT",
    "IS DISTINCT FROM",
    "IS NOT DISTINCT FROM",
    "BETWEEN",
    "NOT BETWEEN",
    "LIKE",
    "NOT LIKE",
    "GLOB",
    "NOT GLOB",
    "REGEXP",
    "NOT REGEXP",
    "MATCH",
    "NOT MATCH",
]


def bitwise_not(in_bytes: bytes) -> bytes:
    buffer = bytearray(in_bytes)
    for i, b in enumerate(buffer):
        buffer[i] = ~b & 0xFF
    return bytes(buffer)


@dataclass
class Expression:
    """Dataclass for SQLite expressions.

    Route indicates what kind of expression is contained.
    """

    route: int = -1
    expr_array: Optional[list["Expression"]] = None
    unary_op: Optional[Union[UnaryOperator, BinaryLiterals]] = None
    lead_expr: Optional[Union["Expression", Literal, ColumnAddress]] = None
    binary_op: Optional[Union[BinaryOperator, BinaryLiterals]] = None
    second_expr: Optional[Union["Expression", Literal, ColumnAddress]] = None
    ternary_op: Optional[typing.Literal["AND", "ESCAPE"]] = None
    third_expr: Optional[Union["Expression", Literal, ColumnAddress]] = None

    def apply_unary_operator(self) -> tuple[bool, "Expression"]:
        """Attempts to apply a unary operator to the leading
        term of the expression. Failure to do so cleanly is a
        no-op.

        First term of output is True if Expression was reduced.
        First term is False if no unary operator was applied."""
        if self.route != 5:
            return False, self
        # Simple statements where unary operator is directly followed by a literal,
        # i.e. +10, NOT TRUE, -3.0
        if (
            (self.unary_op == UnaryOperator.POSITIVE)
            and (self.lead_expr.route == 1)
            and (self.lead_expr.lead_expr.dtype in {int, float})
        ):
            return True, self.lead_expr
        if (
            (self.unary_op == UnaryOperator.NEGATIVE)
            and (self.lead_expr.route == 1)
            and (self.lead_expr.lead_expr.dtype in {int, float})
        ):
            out_expression = self.lead_expr
            out_expression.lead_expr.value *= -1
            return True, out_expression
        if (
            (self.unary_op == UnaryOperator.NOT)
            and (self.lead_expr.route == 1)
            and (self.lead_expr.lead_expr.dtype == bool)
        ):
            out_expression = self.lead_expr
            out_expression.lead_expr.value = not out_expression.lead_expr.value
            return True, out_expression
        if (
            (self.unary_op == UnaryOperator.BITWISE_NOT)
            and (self.lead_expr.route == 1)
            and (self.lead_expr.lead_expr.dtype == bytes)
        ):
            out_expression = self.lead_expr
            out_expression.lead_expr.value = bitwise_not(out_expression.lead_expr.value)
            return True, out_expression
        # Else, assume expression in format like UNARY Expr(Expr(LITERAL) BINARY EXPR(...)...)
        try:
            if (
                (self.unary_op == UnaryOperator.POSITIVE)
                and (self.lead_expr.binary_op is not None)
                and (self.lead_expr.lead_expr.route == 1)
                and (self.lead_expr.lead_expr.lead_expr.dtype in {int, float})
            ):
                return True, self.lead_expr
        except _:
            if (
                (self.unary_op == UnaryOperator.NEGATIVE)
                and (self.lead_expr.binary_op is not None)
                and (self.lead_expr.lead_expr.route == 1)
                and (self.lead_expr.lead_expr.lead_expr.dtype in {int, float})
            ):
                out_expression = self.lead_expr
                out_expression.lead_expr.lead_expr.value *= -1
                return True, out_expression
        except _:
            if (
                (self.unary_op == UnaryOperator.NOT)
                and (self.lead_expr.binary_op is not None)
                and (self.lead_expr.lead_expr.route == 1)
                and (self.lead_expr.lead_expr.lead_expr.dtype == bool)
            ):
                out_expression = self.lead_expr
                out_expression.lead_expr.lead_expr.value = (
                    not out_expression.lead_expr.value
                )
                return True, out_expression
        except _:
            if (
                (self.unary_op == UnaryOperator.BITWISE_NOT)
                and (self.lead_expr.binary_op is not None)
                and (self.lead_expr.lead_expr.route == 1)
                and (self.lead_expr.lead_expr.lead_expr.dtype == bytes)
            ):
                out_expression = self.lead_expr
                out_expression.lead_expr.lead_expr.value = bitwise_not(
                    out_expression.lead_expr.value
                )
                return True, out_expression
        finally:
            return False, self


@dataclass
class InsertStatement:
    table_name: str
    values: list[Expression]
    schema_name: Optional[str] = None
    if_exists: bool = False
    column_names: Optional[list[str]] = None
    alias: Optional[str] = None
