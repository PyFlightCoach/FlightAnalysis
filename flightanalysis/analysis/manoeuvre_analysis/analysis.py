from __future__ import annotations
from dataclasses import dataclass

class AlinmentStage:
    SETUP=0
    PRELIM=1
    SECONDARY=2
    OPTIMISED=3


@dataclass
class Analysis:
    def to_dict(self):
        return {k: (v.to_dict() if hasattr(v, 'to_dict') else v) for k, v in self.__dict__.items()}


