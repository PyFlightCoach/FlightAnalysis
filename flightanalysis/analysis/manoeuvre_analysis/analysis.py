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


    def run_all(self):
        while self.__class__.__name__ != 'Scored':
            new = self.run()
            if new.__class__.__name__ == self.__class__.__name__:
                break
            self = new
        return self

