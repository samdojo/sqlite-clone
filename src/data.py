from avltree import AvlTree


class BaseAccessor:
    def __lt__(self, other):
        raise Exception("< unimplemented")

class Entry:
    pass

class Column:
    tree: AvlTree

    def __init__(self, type, default = None):
        self.type = type
        self.default = default

Table = dict[str, Column]

Schema = dict[str, Table]

class Database(dict[str, Schema]):
    def __init__(self):
        super().__init__({None: Schema()}) # create the default schema
