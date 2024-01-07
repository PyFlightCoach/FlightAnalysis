
from flightdata import Collection, State
from .criteria import Criteria
from .measurement import Measurement
from .results import Results, Result
from typing import Callable, Union
from geometry import Coord
from dataclasses import dataclass
import numpy as np
import pandas as pd

from scipy.signal import butter, filtfilt



@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
        measure - a Measurement constructor
        criteria - takes a Measurement and calculates the score
    """
    measure: Callable[[State, State, Coord], Measurement]
    criteria: Criteria

    def to_dict(self):
        return dict(
            measure=self.measure.__name__,
            criteria=self.criteria.to_dict()
        )

    @property
    def name(self):
        return self.measure.__name__
    
    def __call__(self, fl, tp) -> Result:
        return self.criteria(self.measure.__name__, self.measure(fl, tp))
        


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp) -> Results:
        return Results(el.uid, [dg(fl, tp) for dg in self])
       