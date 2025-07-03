from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass


@dataclass
class Deviation(Criteria):
    """Downgrades the entire sample based on its standard deviation."""
    def __call__(self, vs: npt.NDArray, limits=True):
        error = np.std(vs)
        dg = self.lookup(np.abs(error), limits)
        dgid = len(vs) - 1  
        return np.array([error]), np.array([dg]), np.array([dgid])
