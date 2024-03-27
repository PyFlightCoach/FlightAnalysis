from .analysis import Analysis, AlinmentStage
from .basic import Basic
from .alignment import Alignment
from .complete import Complete, Scored


def parse_dict(data: dict) -> Analysis:
    return Scored.from_dict(data)