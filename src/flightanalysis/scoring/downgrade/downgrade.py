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

from ..reffuncs import measures as me, selectors as se, visors as vi
from ..results import Result
from ..visibility import apply_visibility

from .base import DG


@dataclass
class DownGrade(DG):
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - takes a measurement of the flown data 
    visor - estimate of the visibility of the measurement
    selectors - a set of functions that extract a region of interest from the measurement
    criteria - takes a Measurement and calculates the score
    """
    measure: RefFunc
    visor: RefFunc
    selectors: RefFuncs
    criteria: AnyIntraCriteria
    
    def __repr__(self):
        return f"DownGrade({self.name}, {str(self.measure)}, {str(self.visor)}, {str(self.selectors)}, {str(self.criteria)})"

    def rename(self, name: str):
        return replace(self, name=name)

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            name=self.name,
            tags=self.tags.to_dict() if self.tags else None,
            measure=str(self.measure),
            visor=str(self.visor),
            selectors=self.selectors.to_list(),
            criteria=self.criteria.to_dict(criteria_names),
            unit=self.unit,
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

    def create_sample(self, measurement: npt.NDArray, visibility: npt.NDArray) -> npt.NDArray:
        """create a sample by reducing the measured error to account for the visibility weighting."""
        try:
            if DownGrade.ENABLE_VISIBILITY:
                if isinstance(self.criteria, Deviation):
                    value = measurement - 1
                else:
                    value = measurement
                sample = apply_visibility(
                    self.criteria.prepare(value),
                    visibility,
                    self.criteria.lookup.error_limit,
                    "deviation" if isinstance(self.criteria, ContinuousValue) else "value",
                )
                if isinstance(self.criteria, Deviation):
                    return sample + 1
                else:
                    return sample

            else:
                return self.criteria.prepare(measurement)
        except Exception as e:
            raise Exception(f"Creating sample: {e}") from e
        
    def __call__(
        self,
        el,
        fl: State,
        tp: State,
    ) -> Result:
        try:
            oids, fl, tp = self.select(fl, tp)

            istart = int(np.ceil(oids[0]))
            iend = int(np.ceil(oids[-1]) + 1)

            measurement = self.measure(Elements([el]), fl, tp)

            visibility: npt.NDArray = self.visor(Elements([el]), fl, tp)
            
            sample = self.create_sample(measurement[istart:iend], visibility)

            return Result(
                self.name,
                self.measure.unit,
                measurement,
                visibility,
                sample,
                oids,
                *self.criteria(sample),
                self.criteria,
            )
        except Exception as e:
            raise Exception(f"{self.name}: {e}") from e

def dg(
    name: str,
    meas: RefFunc,
    sels: RefFunc | list[RefFunc],
    criteria: AnyIntraCriteria,
    tags: DGTags,
):
    return DownGrade(name, tags, meas, RefFuncs(sels), criteria)
