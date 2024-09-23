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
            measure=str(self.measure),
            smoothers=self.smoothers.to_list(),
            selectors=self.selectors.to_list(),
            criteria=self.criteria.to_dict(),
            display_name=self.display_name,
        )

    @staticmethod
    def from_dict(data):
        return DownGrade(
            name=data["name"],
            measure=measures.parse(data["measure"]),
            smoothers=smoothers.parse(data["smoothers"]),
            selectors=selectors.parse(data["selectors"]),
            criteria=Criteria.from_dict(data["criteria"]),
            display_name=data["display_name"],
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
            sub_ids = s(fl, sample, **(sekwargs or {}))
            fl = State(fl.data.iloc[ids])
            sample = sample[sub_ids]
            ids = ids[sub_ids]

        return Result(
            self.display_name,
            measurement,
            sample,
            ids,
            *self.criteria(sample, limits),
            self.criteria,
        )


def dg(
    name: str,
    display_name: str,
    measure: RefFunc,
    smoothers: RefFunc | list[RefFunc],
    selectors: RefFunc | list[RefFunc],
    criteria: Criteria,
):
    return DownGrade(
        name, measure, RefFuncs(smoothers), RefFuncs(selectors), criteria, display_name
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
    exits: DownGrades
    line: DownGrades
    roll: DownGrades
    loop: DownGrades
    rolling_loop: DownGrades
    snap: DownGrades
    spin: DownGrades
    stallturn: DownGrades
