from .analysis import Analysis
from .basic import Basic
from .alignment import Alignment
from .complete import Complete, Scored


def parse_dict(data: dict) -> Analysis:
    return Scored.from_dict(data)

def parse(data: dict) -> Basic | Alignment | Complete | Scored:
    if 'parameters' in data:
        return Basic.from_mindict(data).proceed()
    else:
        return parse_dict(data).proceed()