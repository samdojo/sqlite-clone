from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Type, TypeAlias, Union
import typing


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
class UpdateTableStatement:
    pass


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
    pass


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


@dataclass
class InsertStatement:
    table_name: str
    values: list[Expression]
    schema_name: Optional[str] = None
    if_exists: bool = False
    column_names: Optional[list[str]] = None
    alias: Optional[str] = None
