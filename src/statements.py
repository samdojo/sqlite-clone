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
    set_assignments: List[Dict[str, Any]]  # [{'columns': [...], 'expression': ..., 'is_column_list': bool}]
    from_clause: Optional[Any] = None  # TableOrSubQuery
    where_expr: Optional[Any] = None   # Expression
    returning_exprs: Optional[List[Any]] = None  # List[Expression]
    or_action: Optional[str] = None    # "ABORT", "FAIL", "IGNORE", "REPLACE", "ROLLBACK"



@dataclass
class CreateTableStatement:
    table_name: str
    columns: List[Column]



@dataclass
class DropTableStatement:
    table_name: str
    schema_name: Optional[str] = None
    if_exists: bool = False


@dataclass
class SelectStatement:
    pass


@dataclass
class InsertStatement:
    pass


LiteralType: TypeAlias = int | float | bool | str | bytes | None


@dataclass
class Literal:
    """Container for constant value."""

    dtype: type
    value: LiteralType


@dataclass
class Table:
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

