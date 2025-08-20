from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ColumnDefinition:
    name: str
    col_type: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    default_value: Optional[str] = None

class ColumnParser:
    def parse_column(self, col_def: str) -> ColumnDefinition:
        tokens = col_def.strip().split()
        name = tokens[0]
        col_type = tokens[1] if len(tokens) > 1 else None
        
        default_value = None
        if "DEFAULT" in (t.upper() for t in tokens):
            idx = [t.upper() for t in tokens].index("DEFAULT")
            if idx + 1 < len(tokens):
                default_value = tokens[idx + 1]
        
        constraints = [t for t in tokens[2:] if t.upper() != "DEFAULT" and t != default_value]
        
        return ColumnDefinition(name, col_type, constraints, default_value)
