from dataclasses import dataclass
from typing import Optional
@dataclass
class DropTableData:
    table_name: str
    schema_name: Optional[str] = None
    if_exists: bool = False
drop_users_data = DropTableData(
    table_name="users",
    schema_name="public",
    if_exists=True
)
class Catalog:
    def _init_(self):
        self.tables = {"public.users": ["id", "name"]}
    def has_dependencies(self, full_name):
        return False
    def drop_storage(self, full_name):
        print(f"Storage for {full_name} removed.")
class DropTableExecutor:
    def _init_(self, catalog):
        self.catalog = catalog
    def execute(self, drop_data: DropTableData):
        full_name = f"{drop_data.schema_name}.{drop_data.table_name}" if drop_data.schema_name else drop_data.table_name
        if full_name not in self.catalog.tables:
            if drop_data.if_exists:
                print(f"Notice: table {full_name} does not exist, skipping.")
                return
            else:
                raise Exception(f"Error: table {full_name} does not exist.")
        if self.catalog.has_dependencies(full_name):
            raise Exception(f"Error: cannot drop {full_name}, other objects depend on it.")
        del self.catalog.tables[full_name]
        self.catalog.drop_storage(full_name)
        print(f"Table {full_name} dropped successfully.")
catalog = Catalog()
executor = DropTableExecutor(catalog)
executor.execute(drop_users_data)
