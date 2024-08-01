import typing as T
from dataclasses import dataclass, field


@dataclass
class OpenXMLStyle:
    style_id: str
    name: str
    type: str
    default: T.Optional[str] = field(default=None)
