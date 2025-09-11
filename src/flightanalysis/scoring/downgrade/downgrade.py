from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Tuple

from flightanalysis.scoring.criteria.intra.deviation import Deviation
import numpy as np
import numpy.typing as npt
from flightdata import State
from geometry.utils import apply_index_slice

from flightanalysis.base.ref_funcs import RefFunc, RefFuncs

from ..criteria import Bounded, Continuous, ContinuousValue, Criteria, Single
from ..measurement import Measurement
from ..reffuncs import measures as me, selectors as se, smoothers as sm
from ..results import Result
from ..visibility import visibility

from .dg import DG


@dataclass
class DownGrade(DG):
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - a Measurement constructor
    criteria - takes a Measurement and calculates the score
    display_name - the name to display in the results
    selector - the selector to apply to the measurement before scoring
    """

    measure: RefFunc
    smoothers: RefFuncs
    selectors: RefFuncs
    criteria: Bounded | Continuous | Single

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

    def select(self, fl: State, tp: State, **kwargs) -> Tuple[np.ndarray, State, State]:
        """get the indexes of the cropped sample and add datapoint at cropping boundaries"""
        oids = np.arange(len(fl))
        sfl, stp = fl, tp
        for s in self.selectors:
            sli = s(sfl, **kwargs)
            oids = apply_index_slice(oids, sli)
            sfl = sfl.iloc[sli]
            stp = stp.iloc[sli]

        fl = State.stack([fl.iloc[: oids[0]], sfl, fl.iloc[oids[-1] :]])
        tp = State.stack([tp.iloc[: oids[0]], stp, tp.iloc[oids[-1] :]])

        return oids, fl, tp

    def create_sample(self, measurement: Measurement) -> npt.NDArray:
        """create a sample by reducing the measured error to account for the visibility weighting."""
        if DownGrade.ENABLE_VISIBILITY:
            if isinstance(self.criteria, Deviation):
                value = measurement.value - 1
            else:
                value = measurement.value
            sample = visibility(
                self.criteria.prepare(value),
                measurement.visibility,
                self.criteria.lookup.error_limit,
                "deviation" if isinstance(self.criteria, ContinuousValue) else "value",
            )
            if isinstance(self.criteria, Deviation):
                return sample + 1
            else:
                return sample

        else:
            return self.criteria.prepare(measurement.value)

    def smoothing(
        self, sample: npt.NDArray, dt: float, el: str, **kwargs
    ) -> npt.NDArray:
        """Apply the smoothers to the sample"""
        for _sm in self.smoothers:
            sample = _sm(sample, dt, el, **kwargs)
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

        istart = int(np.ceil(oids[0]))
        iend = int(np.ceil(oids[-1]) + 1)

        measurement: Measurement = self.measure(fl, tp, **(mkwargs or {}))[istart:iend]

        raw_sample = self.create_sample(measurement)

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
    sms.append(sm.final())
    return DownGrade(name, meas, RefFuncs(sms), RefFuncs(sels), criteria)
