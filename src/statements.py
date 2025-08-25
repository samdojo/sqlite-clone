from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Type, TypeAlias


@dataclass
class Column:
    name: str
    type: Type
    nullable: bool
    default: Optional[Any]
    primary_key: bool
    unique: bool



@dataclass
class UpdateTableStatement:
    pass


@dataclass
class CreateTableStatement:
    table_name: str
    columns: List[Column]



@dataclass
class DropTableStatement:
    pass


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

    @staticmethod
    def isUnary(value: str) -> bool:
        return value in {k.value for k in UnaryOperator}


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

    @staticmethod
    def isBinary(value: str) -> bool:
        return value in {k.value for k in BinaryOperator}
