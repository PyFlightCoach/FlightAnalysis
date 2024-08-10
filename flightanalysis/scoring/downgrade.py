from __future__ import annotations
from flightdata import Collection, State
from .criteria import Bounded, Continuous, Single, Criteria
from .measurement import Measurement
from .results import Results, Result
from typing import Callable
from geometry import Coord
from dataclasses import dataclass
from flightanalysis.base.ref_funcs import RefFuncs, RefFunc
import numpy as np


@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - a Measurement constructor
    criteria - takes a Measurement and calculates the score
    display_name - the name to display in the results
    selector - the selector to apply to the measurement before scoring
    """

    name: str
    measure: Callable[
        [State, State, Coord], Measurement
    ]  # gets the flown and template measurements
    smoothers: RefFuncs  # smoothes the measurement
    selectors: RefFuncs  # selects the values to downgrade
    criteria: (Bounded | Continuous | Single)  # looks up the downgrades based on the errors
    display_name: str

    def rename(self, name: str):
        return DownGrade(
            name,
            self.measure,
            self.smoothers,
            self.selectors,
            self.criteria,
            self.display_name,
        )

    def to_dict(self):
        return dict(
            name=self.name,
            measure=self.measure.__name__,
            smoothers=self.smoothers.to_list(),
            selectors=self.selectors.to_list(),
            criteria=self.criteria.to_dict(),
            display_name=self.display_name,
        )

    def __call__(self, fl, tp, limits=True) -> Result:
        measurement: Measurement = self.measure(fl, tp)
        
        sample = measurement.value * measurement.visibility
        
        for sm in self.smoothers:
            sample = sm(sample)

        ids = np.arange(len(fl))

        for s in self.selectors:
            sub_ids = s(fl, sample)
            fl = State(fl.data.iloc[ids])
            sample = sample[sub_ids]
            ids = ids[sub_ids]
        
        return Result(
            self.display_name,
            measurement,
            sample,
            ids,
            *self.criteria(sample, limits)
        )


def dg(
    name: str,
    display_name: str,
    measure: Callable,
    smoothers: RefFunc | list[RefFunc],
    selectors: RefFunc | list[RefFunc],
    criteria: Criteria,
):
    return DownGrade(name, measure, RefFuncs(smoothers), RefFuncs(selectors) , criteria, display_name)


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, name, fl, tp, limits=True) -> Results:
        return Results(name, [dg(fl, tp, limits) for dg in self])

    def to_list(self):
        return [dg.name for dg in self]
