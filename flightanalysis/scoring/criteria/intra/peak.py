from __future__ import annotations
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from .. import Criteria



@dataclass
class Peak(Criteria):
    limit: float=0
    """Downgrade the largest value based on its distance above the limit."""
    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        sample = np.maximum(np.abs(vs) - self.limit, 0)
        idx = np.argmax(sample)
        errors = np.array([sample[idx]])
        if errors[0] == 0:
            return np.array([]), np.array([]), np.array([], dtype=int)
        else:
            return errors, self.lookup(errors, limits), np.array([idx])