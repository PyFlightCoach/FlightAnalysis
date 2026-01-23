from __future__ import annotations
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass

from .. import Criteria



@dataclass
class Peak(Criteria):
    limit: float=0
    """Downgrade the largest absolute value based on its distance above the limit"""

    def describe(self, unit: str = "") -> str:
        limit = np.degrees(self.limit) if unit == "radians" else self.limit
        return f"{super().describe()}: Downgrades are assigned to the maximum value in the sample, for its distance above {limit:.2f} {unit}."

    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        idx = np.argmax(vs)
        errors = np.array([vs[idx]])
        if errors[0] == 0:
            return np.array([]), np.array([]), np.array([], dtype=int)
        else:
            return errors, self.lookup(errors, limits), np.array([idx])
    
    def prepare(self, vs):
        return np.maximum(vs - self.limit, 0)

@dataclass
class AbsPeak(Peak):

    def describe(self, unit = ""):
        limit = np.degrees(self.limit) if unit == "radians" else self.limit
        return f"{super().describe()}: Downgrades are assigned to the maximum absolute value in the sample, for its distance above {limit:.2f} {unit}."

    def prepare(self, vs):
        """Downgrade the largest absolute value based on its distance above the limit"""
        return np.maximum(np.abs(vs) - self.limit, 0)


@dataclass
class Trough(Criteria):
    limit: float=0
    """Downgrade the smallest value based on its distance below the limit"""

    def describe(self, unit: str = "") -> str:
        limit = np.degrees(self.limit) if unit == "radians" else self.limit
        return f"{super().describe()}: Downgrades are assigned to the minimum value in the sample, for its distance below {limit:.2f} {unit}."

    def __call__(self, vs: npt.NDArray, limits: bool=True) -> npt.NDArray:
        idx = np.argmin(vs)
        errors = np.array([vs[idx]])
        if errors[0] == 0:
            return np.array([]), np.array([]), np.array([], dtype=int)
        else:
            return errors, self.lookup(errors, limits), np.array([idx])
    
    def prepare(self, vs):
        return np.maximum(self.limit - vs, 0)
    
@dataclass
class AbsTrough(Trough):
    """Downgrade the smallest absolute value based on its distance below the limit"""

    def describe(self, unit: str = "") -> str:
        limit = np.degrees(self.limit) if unit == "radians" else self.limit
        return f"{super().describe()}: Downgrades are assigned to the minimum absolute value in the sample, for its distance below {limit:.2f} {unit}."

    def prepare(self, vs):
        return np.maximum(self.limit - np.abs(vs), 0)
    