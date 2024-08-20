from __future__ import annotations
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from .. import Criteria


@dataclass
class Single(Criteria): 
    """Downgrade all values"""            
    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        errors = np.abs(vs)
        return errors, self.lookup(errors, limits), np.arange(len(vs))
                


@dataclass
class Limit(Criteria):
    """Downgrade the largest value above a threshold"""
    limit: float = 0
    def __call__(self, vs: npt.NDArray, limits: bool=True) -> np.Any:
        errors = np.maximum(np.abs(vs) - self.limit, 0)
        idx = np.arange(len(vs))
        return errors, self.lookup(errors, limits), idx 

    