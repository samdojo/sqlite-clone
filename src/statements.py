from dataclasses import dataclass
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
