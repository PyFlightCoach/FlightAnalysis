from __future__ import annotations
from dataclasses import dataclass
from flightdata import State
from loguru import logger

class AlinmentStage:
    SETUP=0
    PRELIM=1
    SECONDARY=2
    OPTIMISED=3


@dataclass
class Analysis:
    def to_dict(self):
        return {k: (v.to_dict() if hasattr(v, 'to_dict') else v) for k, v in self.__dict__.items()}

    @staticmethod
    def from_dict(data: dict) -> Analysis:
        return Scored.from_dict(data)
    
    def run_all(self):
        while self.__class__.__name__ != 'Scored':
            new = self.run()
            if new.__class__.__name__ == self.__class__.__name__:
                break
            self = new
        return self

    def start(mdef, flown: State, direction: int) -> Analysis:
        return Basic(mdef, flown, direction, AlinmentStage.SETUP)



from .basic import Basic # noqa: E402
from .alignment import  Alignment # noqa: E402
from .complete import Complete, Scored  # noqa: E402