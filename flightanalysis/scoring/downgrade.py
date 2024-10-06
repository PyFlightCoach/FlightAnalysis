from __future__ import annotations
from flightdata import Collection, State
from .criteria import Bounded, Continuous, Single, Criteria, ContinuousValue
from .measurements.measurement import Measurement
from .visibility import visibility
from .results import Results, Result
from dataclasses import dataclass
from flightanalysis.base.ref_funcs import RefFuncs, RefFunc
import numpy as np
from .measurements import measures
from .smoothing import smoothers
from .selectors import selectors


@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - a Measurement constructor
    criteria - takes a Measurement and calculates the score
    display_name - the name to display in the results
    selector - the selector to apply to the measurement before scoring
    """

    name: str
    measure: RefFunc  # measure the flight data
    smoothers: RefFuncs  # smooth the measurement
    selectors: RefFuncs  # select the values to downgrade
    criteria: (
        Bounded | Continuous | Single
    )  # looks up the downgrades based on the errors
    
    def rename(self, name: str):
        return DownGrade(
            name,
            self.measure,
            self.smoothers,
            self.selectors,
            self.criteria,
        )

    def to_dict(self):
        return dict(
            name=self.name,
            measure=str(self.measure),
            smoothers=self.smoothers.to_list(),
            selectors=self.selectors.to_list(),
            criteria=self.criteria.to_dict(),
        )

    @staticmethod
    def from_dict(data):
        return DownGrade(
            name=data["name"],
            measure=measures.parse(data["measure"]),
            smoothers=smoothers.parse(data["smoothers"]),
            selectors=selectors.parse(data["selectors"]),
            criteria=Criteria.from_dict(data["criteria"]),
        )

    def __call__(
        self,
        el,
        fl: State,
        tp: State,
        limits=True,
        mkwargs: dict = None,
        smkwargs: dict = None,
        sekwargs: dict = None,
    ) -> Result:
        measurement: Measurement = self.measure(fl, tp, **(mkwargs or {}))

        sample = visibility(
            self.criteria.prepare(measurement.value),
            measurement.visibility,
            self.criteria.lookup.error_limit,
            "deviation" if isinstance(self.criteria, ContinuousValue) else "value",
        )

        for sm in self.smoothers:
            sample = sm(sample, el, **(smkwargs or {}))

        ids = np.arange(len(fl))

        for s in self.selectors:
            sub_ids = s(
                State(fl.data.iloc[ids]), 
                State(tp.data.iloc[ids]), 
                sample[ids], 
                **(sekwargs or {})
            )
            
            ids = ids[sub_ids]

        return Result(
            self.name,
            measurement,
            sample[ids],
            ids,
            *self.criteria(sample[ids], limits),
            self.criteria,
        )


def dg(
    name: str,
    measure: RefFunc,
    smoothers: RefFunc | list[RefFunc],
    selectors: RefFunc | list[RefFunc],
    criteria: Criteria,
):
    return DownGrade(
        name, measure, RefFuncs(smoothers), RefFuncs(selectors), criteria
    )


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(
        self,
        el: str | any,
        fl,
        tp,
        limits=True,
        mkwargs: dict = None,
        smkwargs: dict = None,
        sekwargs: dict = None,
    ) -> Results:
        return Results(
            el if isinstance(el, str) else el.uid,
            [dg(el, fl, tp, limits, mkwargs, smkwargs, sekwargs) for dg in self],
        )

    def to_list(self):
        return [dg.name for dg in self]


@dataclass
class DowgradeGroups:
    entry_line: DownGrades
    horizontal_line: DownGrades
    inclined_line: DownGrades
    entry_line_before_spin: DownGrades
    line_before_spin: DownGrades
    line_after_spin: DownGrades
    line_before_stallturn: DownGrades
    line_after_stallturn: DownGrades
    horizontal_roll: DownGrades
    inclined_roll: DownGrades
    vplane_loop_exit_horiz: DownGrades
    vplane_loop_exit_inclined: DownGrades
    hplane_loop: DownGrades
    rolling_vplane_loop_exit_horiz: DownGrades
    rolling_vplane_loop_exit_inclined: DownGrades
    rolling_hplane_loop: DownGrades
    snap: DownGrades
    spin: DownGrades
    stallturn: DownGrades
