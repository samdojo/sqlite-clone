from dataclasses import dataclass
from typing import Optional, Self, TypeAlias, Union


@dataclass
class UpdateTableStatement:
    pass


@dataclass
class CreateTableStatement:
    pass


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


@dataclass
class SubQuery:
    """Container for subquery."""

    content: Union[SelectStatement, Self]
    alias: Optional[str] = None
