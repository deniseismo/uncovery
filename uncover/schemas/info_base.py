import json
from dataclasses import asdict, dataclass, astuple
from enum import Enum


@dataclass
class InfoBase(json.JSONEncoder):
    def default(self, o):
        """serialize data © tekore"""
        if isinstance(o, Enum):
            return str(o)
        elif isinstance(o, InfoBase):
            return asdict(o)
        else:
            return super().default(o)

    def __iter__(self):
        return iter(astuple(self))
