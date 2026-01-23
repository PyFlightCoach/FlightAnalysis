from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Comparison(Criteria):

    def describe(self, unit: str = "") -> str:
        return f"{super().describe(unit)}: Used for comparing sequential values for a given parameter. Compares each value to the previous one."

    def __call__(self, vs: npt.NDArray)-> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        """given an array of values
        returns the errors, downgrades and keys"""
        vals = np.abs(np.concatenate([[vs[0]],vs]))
        errors = np.maximum(vals[:-1], vals[1:]) / np.minimum(vals[:-1], vals[1:]) - 1

        return errors, self.lookup(errors), np.arange(len(vs))

free_comparison = Comparison("free_comparison")