from __future__ import annotations
from flightanalysis.elements.tags import DGTags

from dataclasses import dataclass, replace
from typing import Tuple

from flightanalysis.elements.element import Elements
from flightanalysis.scoring.criteria import Deviation, ContinuousValue, AnyIntraCriteria
import numpy as np
import numpy.typing as npt
from flightdata import State
from geometry.utils import apply_index_slice

from flightanalysis.base.ref_funcs import RefFunc, RefFuncs

from ..measurement import Measurement
from ..reffuncs import measures as me, selectors as se, smoothers as sm
from ..results import Result
from ..visibility import visibility

from .base import DG


@dataclass
class DownGrade(DG):
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - a Measurement constructor
    criteria - takes a Measurement and calculates the score
    display_name - the name to display in the results
    selector - the selector to apply to the measurement before scoring
    """

    measure: RefFunc
<<<<<<< HEAD
    smoothers: RefFuncs
=======
>>>>>>> newmeasure
    selectors: RefFuncs
    criteria: AnyIntraCriteria

    def __repr__(self):
<<<<<<< HEAD
        return f"DownGrade({self.name}, {str(self.measure)}, {str(self.smoothers)}, {str(self.selectors)}, {str(self.criteria)})"
=======
        return f"DownGrade({self.name}, {str(self.measure)}, {str(self.selectors)}, {str(self.criteria)})"
>>>>>>> newmeasure

    def rename(self, name: str):
        return replace(self, name=name)

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            name=self.name,
            tags=self.tags.to_dict() if self.tags else None,
            measure=str(self.measure),
<<<<<<< HEAD
            smoothers=self.smoothers.to_list(),
=======
>>>>>>> newmeasure
            selectors=self.selectors.to_list(),
            criteria=self.criteria.to_dict(criteria_names),
        )

    def select(self, fl: State, tp: State, **kwargs) -> Tuple[np.ndarray, State, State]:
        """get the indexes of the cropped sample and add datapoint at cropping boundaries"""
        try:
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
        except Exception as e:
            raise Exception(f"Selector: {e}") from e

    def create_sample(self, measurement: Measurement) -> npt.NDArray:
        """create a sample by reducing the measured error to account for the visibility weighting."""
        try:
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
        except Exception as e:
            raise Exception(f"Creating sample: {e}") from e
        
    def smoothing(
        self, sample: npt.NDArray, dt: float, el: str, **kwargs
    ) -> npt.NDArray:
        """Apply the smoothers to the sample"""
        try:
            for _sm in self.smoothers:
                sample = _sm(sample, dt, el, **kwargs)
            return sample
        except Exception as e:
            raise Exception(f"Smoothing: {e}") from e

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
        try:
<<<<<<< HEAD
            oids, fl, tp = self.select(fl, tp, **(sekwargs or {}))
=======
            meta = {}
            oids, fl, tp = self.select(fl, tp, meta=meta)
>>>>>>> newmeasure

            istart = int(np.ceil(oids[0]))
            iend = int(np.ceil(oids[-1]) + 1)

<<<<<<< HEAD
            measurement: Measurement = self.measure(Elements([el]), fl, tp, **(mkwargs or {}))

            raw_sample = self.create_sample(measurement[istart:iend])

            sample = self.smoothing(raw_sample, fl.dt, el, **(smkwargs or {}))
=======
            measurement = self.measure(Elements([el]), fl, tp, meta=meta)

            visibility: npt.NDArray = self.measure.visor(fl, tp, measurement, meta=meta)
            
            sample = self.create_sample(measurement.value, visibility)[istart:iend]
>>>>>>> newmeasure

            return Result(
                self.name,
                measurement,
                raw_sample,
                sample,
                oids,
                *self.criteria(sample, limits),
                self.criteria,
                meta
            )
        except Exception as e:
            raise Exception(f"{self.name}: {e}") from e

def dg(
    name: str,
    meas: RefFunc,
    sms: RefFunc | list[RefFunc],
    sels: RefFunc | list[RefFunc],
    criteria: AnyIntraCriteria,
    tags: DGTags,
):
    return DownGrade(name, tags, meas, RefFuncs(sms), RefFuncs(sels), criteria)
