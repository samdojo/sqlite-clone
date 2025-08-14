from dataclasses import dataclass
from typing import Any, List, Optional, Type


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
