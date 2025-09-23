from typing import Any, Generic, ItemsView, Iterator, KeysView, Literal, Mapping, NamedTuple, Optional, TypeVar, ValuesView
from avltree import AvlTree
import itertools

from baseexecuter import ExecutingException
from statements import Expression, LiteralType, Literal as LitExpr
from collections import namedtuple


class Entry(Mapping):
    """A table row based off a NamedTuple.

    Entries should not be created directly. Each Table
    contains a constructor for an Entry with the appropriate
    columns which are the same as the namedtuple's fields.
    Entry implements both indexing on the position of a field
    and on the field's name."""
    row: NamedTuple

    def __init__(self, row: NamedTuple):
        self.row = row

    def _replace(self, **kwargs: dict[str, Any]) -> "Entry":
        """Construct a new row using an existing Entry
        and a map of Entry fields to their new values
        to replace the existing values. The existing
        Entry is not mutated and a new Entry is created."""
        return Entry(row=self.row._replace(**kwargs))

    def __getitem__(self, key: int | str):
        """Implements indexing on both position indices
        and field names."""
        if isinstance(key, int):
            return self.row[key]
        return getattr(self.row, key)

    def __len__(self) -> int:
        return len(self.row)

    def __iter__(self) -> Any:
        return self.row.__iter__()

    def __eq__(self, other: object, /) -> bool:
        return self.row == other

    def __ne__(self, value: object, /) -> bool:
        return self.row.__ne__(value)

    def __contains__(self, key: object) -> bool:
        return key in self.row._fields

    def __repr__(self) -> str:
        return repr(self.row)

    def keys(self) -> KeysView[str]:
        return self.row._asdict().keys()
    
    def values(self) -> ValuesView[Any]:
        return self.row._asdict().values()

    def items(self) -> ItemsView[str, Any]:
        return self.row._asdict().items()

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self.row._fields:
            return default
        return self[key]


C = TypeVar("C", bound=LiteralType)

class Column(Generic[C]):
    """A column for a DB table containing data of some type C,
    where C is a LiteralType.

    Stores data such as the type of the column, the default value,
    and a binary tree to search and access Entries based off of a
    given Column value. Exposes some methods from the underlying
    binary tree, such as the ability to iterate over the Column
    keys (the Entry values corresponding belonging to only this
    Column), the between method to find all keys in a given range,
    and minimum and maximum to find the least or greatest values.
    Note that if any Entries contain None for this Column, None
    will not appear in the between, minimum, or maximum methods
    but will appear when iterating over the class.

    Altering the entries associated with a Column should not be
    done at the Column level. This should instead be managed by
    methods at the Table-level to ensure all Columns under a table
    contain references to the same set of rows."""
    tree: AvlTree[C, list[Entry]]
    none_entries: list[Entry]

    def __init__(self, type: type[C], default: Optional[C] = None):
        self.type = type
        self.default: Optional[C] = default
        self.tree = AvlTree()
        self.none_entries = []

    def append(self, key: C, entry: Entry):
        """Adds an Entry to the Column."""
        if key is None:
            self.none_entries.append(entry)
            return
        if key not in self.tree:
            self.tree[key] = list()
        self.tree[key].append(entry)

    def __iter__(self) -> Iterator[C]:
        if len(self.none_entries) > 0:
            return itertools.chain(self.tree.between(), [None])
        return self.tree.between()

    def __getitem__(self, key: C) -> list[Entry]:
        if key is None:
            return self.none_entries
        return self.tree[key]

    def get(self, key: C) -> list[Entry]:
        """Safe method for retrieving all entries indexed by a given key.

        If a no entries are associated with a given key yet in the Column's
        binary tree, will return an empty list instead of raising a KeyError."""
        if key is None:
            return self.none_entries
        return self.tree.get(key, list())

    def __delitem__(self, key: C):
        if key is None:
            self.none_entries = []
        else:
            del self.tree[key]

    def between(
        self,
        start: C = None,
        stop: C = None,
        treatment: Literal["inclusive", "exclusive"] = "inclusive",
    ) -> Iterator[C]:
        return self.tree.between(start, stop, treatment)

    def minimum(self) -> C:
        return self.tree.minimum()

    def maximum(self) -> C:
        return self.tree.maximum()


class Table:
    """Dict-like class aggregating a set of columns.

    All Columns should be added to Table prior to
    attempting to add any Entries to Columns. Entries
    should not be added directly to any Columns, all
    new entries should be created by submitting data to
    Table's add_entry method which will add a reference
    to the entry to every Column in the table, handle
    data type validation, and apply Column defaults."""
    tbl: dict[str, Column]
    ordered_columns: list[str]
    entry_type: type

    def __init__(self, column_list: list[str], map: Optional[dict[str, Column]] = None):
        self.tbl = {} if map is None else map
        self.ordered_columns = column_list
        self.entry_type = namedtuple("Entry", column_list)

    def __setitem__(self, key: str, value: Column):
        self.tbl[key] = value

    def __getitem__(self, key: str) -> Column:
        return self.tbl[key]

    def __delitem__(self, key: str):
        del self.tbl[key]

    def __len__(self) -> int:
        return len(self.tbl)

    @classmethod
    def from_dict(cls, schema: dict[str, Column]) -> 'Table':
        tbl = Table(column_list=list(schema.keys()))
        for k, col in schema.items():
            tbl[k] = col
        return tbl

    def create_entry(self, entry: dict[str, LitExpr]) -> Entry:
        """Entry constructor method. Use over directly
        constructing an Entry since Entry is an immutable tuple,
        and Entry's schema is associated with the table the Entry
        belongs to."""
        entry_data = {}
        for col in self.ordered_columns:
            if col in entry:
                value = entry[col].value
                if value is not None and not isinstance(value, self[col].type):
                    raise ExecutingException(
                        f"Attempted to add value of type {type(value)}: value {value} to column expecting type {self[col].type}"
                    )
            else:
                value = self[col].default
            entry_data[col] = value
        return Entry(row=self.entry_type(**entry_data))

    def add_row(self, entry_data: dict[str, LitExpr]):
        """Takes in data and constructs an Entry which is added to
        every column in the Table.

        You can pass in only a subset of all available columns on the
        table and add_row will apply any relevant defaults and
        validate that the data passed for each column is of the appropriate
        data type."""
        if len(set(entry_data.keys()) - set(self.ordered_columns)) != 0:
            raise ExecutingException(
                f"Columns {list(set(entry_data.keys()) - set(self.ordered_columns))} included in INSERT statement but do not exist in Table."
            )
        entry = self.create_entry(entry_data)
        self.insert_entry(entry)

    def insert_entry(self, entry: Entry):
        for name, col in self.tbl.items():
            col.append(entry[name], entry)

    # TODO: Need to add test
    def delete_entry(self, entry: Entry):
        for c in self.ordered_columns:
            column = self[c]
            entries = column.get(entry[c])
            idx = safe_index_entries(entries, entry)
            if (len(entries) == 0) or (idx < 0):
                continue
            entries.pop(idx)

    # TODO: Need to add test
    def update_entry(self, old: Entry, new: Entry):
        self.delete_entry(old)
        self.insert_entry(new)

    def keys(self):
        return self.tbl.keys()

    def get_rows(self) -> list[Entry]:
        """Returns all Entries stored within the given table.

        Relies on the fact that all Columns should contain the same
        entries to retrieve the list of entries from the first column."""
        first_col = self[self.ordered_columns[0]]
        entries = []
        for key in first_col:
            entries.extend(first_col[key])
        return entries



def safe_index_entries(lst: list[Entry], entry: Entry) -> int:
    try:
        return lst.index(entry)
    except ValueError:
        return -1

Schema = dict[str, Table]


class Database(dict[str, Schema]):
    """Top-level container in a series of classes.

    Each database can contain multiple schema,
    which can contain multiple tables,
    which can contain multiple columns,
    which contain references to Entry instances or rows."""
    def __init__(self):
        super().__init__({None: Schema()})  # create the default schema
