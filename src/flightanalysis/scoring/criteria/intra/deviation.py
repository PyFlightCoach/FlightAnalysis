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

    def describe(self, unit: str = "") -> str:
        return f"{super().describe()}: Downgrades are assigned based on the coefficient of variation (standard deviation divided by the mean) of the entire sample."

    def __call__(self, vs: npt.NDArray):
        error = np.std(vs) / np.mean(vs)
        dg = self.lookup(np.abs(error))
        dgid = len(vs) - 1
        return np.array([error]), np.array([dg]), np.array([dgid])


@dataclass
class Total(Criteria):
    """downgrade for the sum of the array."""

    def describe(self, unit: str = "") -> str:
        return f"{super().describe()}: Downgrades are assigned based on the sum of the absolute sample."

    def __call__(self, vs: npt.NDArray):
        error = np.sum(np.abs(vs)) / len(vs)
        dg = self.lookup(error)
        dgid = len(vs) - 1
        return np.array([error]), np.array([dg]), np.array([dgid])
