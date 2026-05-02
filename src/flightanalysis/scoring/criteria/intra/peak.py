from __future__ import annotations

import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from flightanalysis.base.utils import display_unit
from .. import Criteria


@dataclass
class Peak(Criteria):
    limit: float = 0
    direction: int = (
        1  # 1 for distance above the limit, -1 for distance below the limit
    )

    def __call__(self, vs: npt.NDArray, **kwargs) -> npt.NDArray:
        idx = np.argmax(vs)
        errors = np.array([vs[idx]])
        if errors[0] == 0:
            return np.array([]), np.array([]), np.array([], dtype=int)
        else:
            return errors, self.lookup(errors), np.array([idx])

    def prepare(self, vs):
        return np.maximum(self.direction * (vs - self.limit), 0)

    def describe(self, unit: str = "") -> str:
        return f"{super().describe()}: One downgrade is assigned to the value furthest  {'above' if self.direction == 1 else 'below'} {display_unit(self.limit, unit)}."

    def short_description(self, unit: str = "") -> str:
        return f"Peak {'above' if self.direction == 1 else 'below'} {display_unit(self.limit, unit)})"


@dataclass
class AbsPeak(Peak):
    def prepare(self, vs):
        return np.maximum(
            self.direction * (np.abs(vs) - self.limit),
            0,
        )

    def describe(self, unit: str = "") -> str:
        return f"{super().describe()}: One downgrade is assigned to the absolute value furthest  {'above' if self.direction == 1 else 'below'} {display_unit(self.limit, unit)}."

    def short_description(self, unit: str = "") -> str:
        return f"AbsPeak {'above' if self.direction == 1 else 'below'} {display_unit(self.limit, unit)})"


@dataclass
class Trough(Criteria):
    limit: float = 0
    direction: int = (
        -1
    )  # 1 for distance above the limit, -1 for distance below the limit

    def __call__(self, vs: npt.NDArray, **kwargs) -> npt.NDArray:
        idx = np.argmin(vs)
        errors = np.array([vs[idx]])
        if errors[0] == 0:
            return np.array([]), np.array([]), np.array([], dtype=int)
        else:
            return errors, self.lookup(errors), np.array([idx])

    def prepare(self, vs):
        return np.maximum(self.direction * (vs - self.limit), 0)




@dataclass
class AbsTrough(Trough):
    """Downgrade the smallest absolute value based on its distance below the limit"""

    def prepare(self, vs):
        return np.maximum(self.direction * (np.abs(vs) - self.limit), 0)

    def describe(self, unit: str = "") -> str:
        return f"AbsTrough: One downgrade is assigned to the {'largest' if self.direction == 1 else 'smallest'} absolute value for its distance {'below' if self.direction == 1 else 'above'} {display_unit(self.limit, unit)}."

    def short_description(self, unit: str = "") -> str:
        return f"AbsTrough {'above' if self.direction == 1 else 'below'} {display_unit(self.limit, unit)})"
