from dataclasses import dataclass
from typing import TypeAlias

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
