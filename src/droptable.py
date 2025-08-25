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
