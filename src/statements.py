from dataclasses import dataclass
from typing import List, Optional, Self, Union


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


@dataclass
class Table:
    """
    Table container to store the table name, schema name and alias.
    """

    table_name: str
    schema_name: Optional[str]
    alias: Optional[str]


@dataclass
class SubQuery:
    content: Union[SelectStatement, Self]
    alias: Optional[str] = None
