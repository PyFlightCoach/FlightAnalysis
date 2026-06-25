from __future__ import annotations
from typing import Tuple, Literal
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

    def __call__(self, vs: npt.NDArray) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        error = np.std(vs) / np.mean(vs)
        dg = self.lookup(np.abs(error))
        dgid = len(vs) - 1
        return np.array([error]), np.array([dg]), np.array([dgid])

    def local_error(sample: npt.NDArray, dt: npt.NDArray, direction: Literal["forward", "backward"] = "forward") -> npt.NDArray:
        """The value of the error (coefficient of variation) if the sample were to be cut at each point in time.
        if direction is forward, the sample starts at the start and goes to the point.
        if backward it starts at the point and goes to the end of the sample. 
        """
        if direction == "forward":
            return np.abs(sample - np.cumsum(sample) / (np.arange(len(sample)) + 1))
        elif direction == "backward":
            return np.abs(sample - np.cumsum(sample[::-1]) / (np.arange(len(sample)) + 1))[::-1]
        else:
            raise ValueError("direction must be 'forward' or 'backward'")

@dataclass
class Total(Criteria):
    """downgrade for the sum of the array."""

    def describe(self, unit: str = "") -> str:
        return f"{super().describe()}: Downgrades are assigned based on the area under the sample."

    def __call__(self, vs: npt.NDArray, dt: npt.NDArray) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        error = np.sum(np.abs(vs) * dt)
        dg = self.lookup(error)
        dgid = len(vs) - 1
        return np.array([error]), np.array([dg]), np.array([dgid])

    def local_error(sample: npt.NDArray, dt: npt.NDArray, direction: Literal["forward", "backward"] = "forward") -> npt.NDArray:
        """The value of the error (area under the curve) if the sample were to be cut at each point in time.
        if direction is forward, the sample starts at the start and goes to the point.
        if backward it starts at the point and goes to the end of the sample. 
        """
        if direction == "forward":
            return np.cumsum(np.abs(sample) * dt)
        elif direction == "backward":
            return np.cumsum(np.abs(sample[::-1]) * dt[::-1])[::-1]
        else:
            raise ValueError("direction must be 'forward' or 'backward'")