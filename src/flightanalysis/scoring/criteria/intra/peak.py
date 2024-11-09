from __future__ import annotations
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from .. import Criteria



@dataclass
class Peak(Criteria):
    limit: float=0
    """Downgrade the largest absolute value based on its distance above the limit."""
    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        idx = np.argmax(vs)
        errors = np.array([vs[idx]])
        if errors[0] == 0:
            return np.array([]), np.array([]), np.array([], dtype=int)
        else:
            return errors, self.lookup(errors, limits), np.array([idx])
    
    def prepare(self, vs):
        return np.maximum(np.abs(vs) - self.limit, 0)
    

@dataclass
class Trough(Criteria):
    limit: float=0
    """Downgrade the largest absolute value based on its distance below the limit."""
    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        idx = np.argmin(vs)
        errors = np.array([vs[idx]])
        if errors[0] == 0:
            return np.array([]), np.array([]), np.array([], dtype=int)
        else:
            return errors, self.lookup(errors, limits), np.array([idx])
    
    def prepare(self, vs):
        return np.maximum(self.limit - np.abs(vs), 0)