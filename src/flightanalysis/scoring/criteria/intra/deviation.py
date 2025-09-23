from __future__ import annotations
import numpy as np
import numpy.typing as npt

from .. import Criteria
from dataclasses import dataclass


@dataclass
class Deviation(Criteria):
    """Downgrades the entire sample based on the coefficiant of variation.
    (standard deviation / mean) of the input values.
    """
    def __call__(self, vs: npt.NDArray, limits=True):
        error = np.std(vs) / np.mean(vs)
        dg = self.lookup(np.abs(error), limits)
        dgid = len(vs) - 1  
        return np.array([error]), np.array([dg]), np.array([dgid])



@dataclass
class Total(Criteria):
    """downgrade for the sum of the array."""
    def __call__(self, vs: npt.NDArray, limits=True):
        error = np.sum(np.abs(vs)) / len(vs)
        dg = self.lookup(error, limits)
        dgid = len(vs) - 1  
        return np.array([error]), np.array([dg]), np.array([dgid])
    
