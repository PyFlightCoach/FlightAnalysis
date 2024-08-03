from flightdata import Collection, State
from .criteria import Bounded, ContAbs, ContRat, Single
from .measurement import Measurement
from .results import Results, Result
from typing import Callable
from geometry import Coord
from dataclasses import dataclass
from .subsetters import Subsetter
import numpy as np


@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - a Measurement constructor
    criteria - takes a Measurement and calculates the score
    display_name - the name to display in the results
    subsetter - the subsetter to apply to the measurement before scoring
    """

    name: str
    measure: Callable[[State, State, Coord], Measurement]
    criteria: Bounded | ContAbs | ContRat | Single
    display_name: str = None
    subsetter: Subsetter = None

    def to_dict(self):
        return dict(
            name=self.name,
            measure=self.measure.__name__,
            criteria=self.criteria.to_dict(),
            display_name=self.display_name,
            subsetter=str(self.subsetter) if self.subsetter else "all",
        )

    def __call__(self, fl, tp, limits=True) -> Result:
        return self.criteria(
            self.display_name if self.display_name else self.name,
            self.measure(fl, tp),
            self.subsetter(fl) if self.subsetter else np.arange(len(fl)),
            limits,
        )


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, name, fl, tp, limits=True) -> Results:
        return Results(name, [dg(fl, tp, limits) for dg in self])

    def to_list(self):
        return [dg.name for dg in self]
