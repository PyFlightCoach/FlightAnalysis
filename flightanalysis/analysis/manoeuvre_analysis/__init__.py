

from .analysis import Analysis
from .basic import Basic
from .alignment import Alignment
from .complete import Complete
from .scored import Scored

def from_dict(data: dict) -> Basic | Alignment | Complete | Scored:
    return Scored.from_dict(data)

from .schema import MA