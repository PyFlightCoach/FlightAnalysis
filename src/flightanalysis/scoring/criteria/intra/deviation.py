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

    def __call__(self, vs: npt.NDArray, **kwargs) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        error = np.std(vs) / np.mean(vs)
        dg = self.lookup(np.abs(error))
        dgid = len(vs) - 1
        return np.array([error]), np.array([dg]), np.array([dgid])

    def local_downgrade(
        self, sample: npt.NDArray, dt: npt.NDArray, direction: Literal["left", "right"]
    ) -> npt.NDArray:
        """The value of the error (coefficient of variation) if the sample were to be cut at each point in time.
        direction indicates the side of the sample that is being cropped.
        """
        _s = sample if direction == "right" else sample[::-1]
        counts = np.arange(1, len(_s)+1)

        mean = np.cumsum(_s) / counts
        variance = np.cumsum(_s**2) / counts - mean**2

        # avoid tiny negative values from floating point
        variance = np.maximum(variance, 0)

        sd = np.sqrt(variance)
        cv = sd / mean

        return self.lookup(cv if direction == "right" else cv[::-1])


@dataclass
class Total(Criteria):
    """downgrade for the sum of the array."""

    def describe(self, unit: str = "") -> str:
        return f"{super().describe()}: Downgrades are assigned based on the area under the sample."

    def __call__(
        self, vs: npt.NDArray, dt: npt.NDArray, **kwargs
    ) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        error = np.sum(np.abs(vs) * dt)
        dg = self.lookup(error)
        dgid = len(vs) - 1
        return np.array([error]), np.array([dg]), np.array([dgid])

    def local_downgrade(
        self, sample: npt.NDArray, dt: npt.NDArray, direction: Literal["left", "right"]
    ) -> npt.NDArray:
        """The value of the error (area under the curve) if the sample were to be cut at each point in time."""
        if direction == "right":
            return self.lookup(np.cumsum(np.abs(sample) * dt))
        elif direction == "left":
            return self.lookup(np.cumsum(np.abs(sample[::-1]) * dt[::-1])[::-1])
        else:
            raise ValueError("direction must be 'right' or 'left'")
