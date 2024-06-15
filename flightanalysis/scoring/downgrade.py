
from flightdata import Collection, State
from .criteria import Bounded, ContAbs, ContRat, Single
from .measurement import Measurement
from .results import Results, Result
from typing import Callable
from geometry import Coord
from dataclasses import dataclass


@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
        measure - a Measurement constructor
        criteria - takes a Measurement and calculates the score
    """
    measure: Callable[[State, State, Coord], Measurement]
    criteria: Bounded | ContAbs | ContRat | Single

    def to_dict(self):
        return dict(
            measure=self.measure.__name__,
            criteria=self.criteria.to_dict()
        )

    @property
    def name(self):
        return self.measure.__name__
    
    def __call__(self, fl, tp, limits=True) -> Result:
        return self.criteria(self.measure.__name__, self.measure(fl, tp), limits)
        


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, limits=True) -> Results:
        return Results(el.uid, [dg(fl, tp, limits) for dg in self])
       