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
    """Downgrade based on the distance above a limit"""
    limit: float = 0
    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        idx = np.arange(len(vs))
        return vs, self.lookup(vs, limits), idx 

    def prepare(self, vs):
        return np.maximum(np.abs(vs) - self.limit, 0)

@dataclass
class Threshold(Criteria):
    """downgrade based on the distance below the limit"""
    limit: float = 0
    def __call__(self, vs: npt.NDArray, limits: bool=False) -> npt.NDArray:
        idx = np.arange(len(vs))
        return vs, self.lookup(vs, limits), idx 

    def prepare(self, vs):
        return np.maximum(self.limit - np.abs(vs), 0)
