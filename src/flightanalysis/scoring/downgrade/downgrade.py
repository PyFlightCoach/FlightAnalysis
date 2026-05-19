from __future__ import annotations
from flightanalysis.elements.tags import DGTags

from dataclasses import dataclass, replace
from typing import Tuple

from loguru import logger

from flightanalysis.elements.element import Elements
from flightanalysis.scoring.criteria import Deviation, AnyIntraCriteria, AnyDeviationCriteria
import numpy as np
import numpy.typing as npt
from flightdata import State
from geometry.utils import apply_index_slice

from flightanalysis.base.ref_funcs import RefFunc, RefFuncs

from ..reffuncs import measures as me, selectors as se, visors as vi
from ..results import Result
from ..visibility import apply_visibility

from .base import DG

class SquashError(Exception):
    pass


@dataclass
class DownGrade(DG):
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
    measure - takes a measurement of the flown data 
    visor - estimate of the visibility of the measurement
    selectors - a set of functions that extract a region of interest from the measurement
    criteria - takes a Measurement and calculates the score
    """
    measure: RefFunc
    selectors: RefFuncs
    criteria: AnyIntraCriteria
    
    def __repr__(self):
        return f"DownGrade({self.name}, {str(self.measure)}, {str(self.selectors)}, {str(self.criteria)})"

    def rename(self, name: str):
        return replace(self, name=name)

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            name=self.name,
            display_name=self.display_name,
            tags=self.tags.to_dict() if self.tags else None,
            measure=str(self.measure),
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
            if len(oids) > 0:
                fl = State.splice([fl, fl.iloc[oids]])
                tp = State.splice([tp, tp.iloc[oids]])
                
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
                    "deviation" if isinstance(self.criteria, AnyDeviationCriteria) else "value",
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
            meta = {}
            oids, fl, tp = self.select(fl, tp, meta=meta)
            if len(oids) == 0:
                raise SquashError("No data selected by selectors")
            
            _oids = oids.copy()
            _oids[0] = int(np.ceil(oids[0]))
            _oids[-1] = int(np.ceil(oids[-1]) + (0 if _oids[0] == oids[0] else 1)) 
            
            measurement = self.measure(Elements([el]), fl, tp, meta=meta)

            visibility: npt.NDArray = self.measure.visor(fl, tp, measurement, meta=meta)
            
            sample = self.create_sample(measurement.value, visibility)[_oids.astype(int)]

            return Result(
                self.name,
                measurement,
                visibility,
                sample,
                oids,
                *self.criteria(sample, dt=fl.dt[_oids.astype(int)]),
                self.criteria,
                meta
            )
        except (SquashError, Exception) as e:
            if type(e) is SquashError:
                raise e
            else:
                raise Exception(f"{self.name}: {e}") from e

    def markdown(self, rule: str, description: str | None = None) -> str:

        def var_to_title(var: str) -> str:
            return var.replace("_", " ").title()
        
        odata = [f"# {rule.upper()} {var_to_title(self.name)}"]

        if description is not None:
            odata.append(description)

        odata.append(f"### Measurement: {var_to_title(self.measure.__name__)}\n{self.measure.description}")

        odata.append(f"### Visibility: {var_to_title(self.measure.visor.__name__)}\n{self.measure.visor.description}")

        if len(self.selectors) > 0:
            _seldata = []
            _seldata.append("### Selectors")
            for i, sel in enumerate(self.selectors, 1):
                _seldata.append(f"- {var_to_title(sel.__name__)}\n{sel.description}")
            odata.extend("\n".join(_seldata))

        odata.append(f"### Criteria: {self.criteria.__class__.__name__}\n{self.criteria.describe().split(":")[1]}")

        odata.append("### Applicability")
        for k, v in self.tags.to_dict().items():
            odata.append(f"{k}: {v}\n")

        return "\n".join(odata)

def dg(
    name: str,
    display_name: str | None,
    meas: RefFunc,
    sels: RefFunc | list[RefFunc],
    criteria: AnyIntraCriteria,
    tags: DGTags,
):
    return DownGrade(name, display_name, tags, meas, RefFuncs(sels), criteria)
