from __future__ import annotations
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from .. import Criteria


@dataclass
class Single(Criteria):             
    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        errors = np.abs(vs)
        return errors, self.lookup(errors, limits), np.arange(len(vs))
                

