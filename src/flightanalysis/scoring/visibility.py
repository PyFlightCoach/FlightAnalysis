import numpy as np
import numpy.typing as npt
from typing import Literal


def _apply_visibility(x: npt.NDArray, v: npt.NDArray):
    """Equation of a circle that passes through (1,1) and (0,0), 
    the gradient of the circumference at (0,0) is equal to v"""
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.sqrt((v**2 + 1) / (v - 1) ** 2)
        xc = v / (v - 1)
        yc = 1 / (1 - v)
        y = yc - np.sqrt(-(xc**2) + 2 * xc * x + r**2 - x**2)
        y = np.where(y<=0, 0, y)
        return np.nan_to_num(np.where(x > 1, x, y), nan=x)

def apply_visibility(
    val: float | npt.NDArray,
    weighting: float,
    limit: float,
    kind: Literal["deviation", "value"] = "value",
) -> npt.NDArray:
    if kind == "value":
        x = np.abs(val / limit)
    elif kind == "deviation":
        diff = np.insert(np.diff(val), 0, 0.0, axis=0)
        x = np.abs(diff / limit)

    y = _apply_visibility(np.atleast_1d(x), weighting)

    if kind == "value":
        sample = y * limit
    elif kind == "deviation":
        smoothed = (y * limit * np.sign(diff)).cumsum() 
        sample = smoothed - np.mean(smoothed) + np.mean(val)

    return sample

