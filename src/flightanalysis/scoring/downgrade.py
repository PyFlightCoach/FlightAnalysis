from __future__ import annotations

from dataclasses import dataclass, replace
from typing import ClassVar, Tuple

import numpy as np
import numpy.typing as npt
from flightdata import Collection, State
from geometry.utils import apply_index_slice

from flightanalysis.base.ref_funcs import RefFunc, RefFuncs

from .criteria import Bounded, Continuous, ContinuousValue, Criteria, Single
from .measurement import Measurement
from .reffuncs import measures, selectors, smoothers
from .results import Result, Results
from .visibility import visibility


@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - a Measurement constructor
    criteria - takes a Measurement and calculates the score
    display_name - the name to display in the results
    selector - the selector to apply to the measurement before scoring
    """

    name: str
    measure: RefFunc  
    smoothers: RefFuncs  
    selectors: RefFuncs  
    criteria: Bounded | Continuous | Single
    ENABLE_VISIBILITY: ClassVar[bool] = True

    def __repr__(self):
        return f"DownGrade({self.name}, {str(self.measure)}, {str(self.smoothers)}, {str(self.selectors)}, {str(self.criteria)})"

    def rename(self, name: str):
        return replace(self, name=name) 

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            name=self.name,
            measure=str(self.measure),
            smoothers=self.smoothers.to_list(),
            selectors=self.selectors.to_list(),
            criteria=self.criteria.to_dict(criteria_names),
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

    def select(self, fl: State, tp: State, **kwargs) -> Tuple[np.ndarray, State, State]:
        """Select the values to downgrade based on the selectors"""
        oids = np.arange(len(fl))
        for s in self.selectors:
            sli = s(fl, **kwargs)
            oids = apply_index_slice(oids, sli)
            fl = fl.iloc[sli]
            tp = tp.iloc[sli]
        return oids, fl, tp

    def visibility(self, measurement: Measurement) -> npt.NDArray:
        """Calculate the visibility of the measurement"""
        if DownGrade.ENABLE_VISIBILITY:
            return visibility(
                self.criteria.prepare(measurement.value),
                measurement.visibility,
                self.criteria.lookup.error_limit,
                "deviation" if isinstance(self.criteria, ContinuousValue) else "value",
            )            
        else:
            return self.criteria.prepare(measurement.value)

    def smoothing(self, sample: npt.NDArray, dt: float, el: str, **kwargs) -> npt.NDArray:
        """Apply the smoothers to the sample"""
        for sm in self.smoothers:
            sample = sm(sample, dt, el, **kwargs)
        return sample

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

        oids, fl, tp = self.select(fl, tp, **(sekwargs or {}))
        measurement: Measurement = self.measure(fl, tp, **(mkwargs or {}))
        raw_sample = self.visibility(measurement)
        sample = self.smoothing(raw_sample, fl.dt, el, **(smkwargs or {}))

        return Result(
            self.name,
            measurement,
            raw_sample,
            sample,
            oids,
            *self.criteria(sample, limits),
            self.criteria,
        )
    

def dg(
    name: str,
    meas: RefFunc,
    sms: RefFunc | list[RefFunc],
    sels: RefFunc | list[RefFunc],
    criteria: Criteria,
):
    if sms is None:
        sms = []
    elif isinstance(sms, RefFunc):
        sms = [sms]
    sms.append(smoothers.final())
    return DownGrade(
        name, meas, RefFuncs(sms), RefFuncs(sels), criteria
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

