from __future__ import annotations
from dataclasses import dataclass
from flightanalysis.definition import ScheduleInfo

@dataclass
class Analysis:

    def to_mindict(self, sinfo: ScheduleInfo):
        return {
            "sinfo": sinfo.__dict__,
        }
        

