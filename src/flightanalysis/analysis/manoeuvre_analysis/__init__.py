

from .analysis import Analysis
from .basic import Basic
from .alignment import Alignment
from .complete import Complete
from .scored import Scored

from schemas import MA


def from_dict(data: dict | MA) -> Basic | Alignment | Complete | Scored:
    return Scored.from_dict(data.model_dump() if isinstance(data, MA) else data)

