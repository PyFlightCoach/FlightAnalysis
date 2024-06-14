from __future__ import annotations
from dataclasses import dataclass
from flightanalysis.definition import ScheduleInfo

@dataclass
class Analysis:
    id: int

    def to_dict(self):
        return {k: (v.to_dict() if hasattr(v, 'to_dict') else v) for k, v in self.__dict__.items()}

    def to_mindict(self, sinfo: ScheduleInfo):
        return {
            "sinfo": sinfo.__dict__,
        }
        
