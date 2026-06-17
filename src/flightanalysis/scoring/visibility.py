import numpy as np
import pandas as pd
import numpy.typing as npt
from typing import Literal, overload


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


@overload
def apply_visibility(
    val: float,
    weighting: float,
    limit: float,
    kind: Literal["deviation", "value"] = "value",
) -> float: ...


@overload
def apply_visibility(
    val: npt.NDArray,
    weighting: float,
    limit: float,
    kind: Literal["deviation", "value"] = "value",
) -> npt.NDArray: ...


def apply_visibility(
    val: float | npt.NDArray,
    weighting: float,
    limit: float,
    kind: Literal["deviation", "value"] = "value",
) -> float | npt.NDArray:
    if kind == "value":
        x = np.abs(val / limit)
    elif kind == "deviation":
        diff = np.insert(np.diff(val), 0, 0.0, axis=0)
        x = np.abs(diff / limit)

    x = np.atleast_1d(x)

    y = _apply_visibility(x, weighting)

    if kind == "value":
        sample = y * limit
    elif kind == "deviation":
        smoothed = (y * limit * np.sign(diff)).cumsum() 
        sample = smoothed - np.mean(smoothed) + np.mean(val)

    if val.ndim == 0:
        return sample[0]
    else:
        return sample


def old_apply_visibility(
    val, weighting: float, limit: float, kind: Literal["deviation", "value"] = "value"
):
    """weighting between 0 and 1"""

    with np.errstate(divide="ignore"):
        b = 1 / weighting

    # res = (val / limit)**(1/weighting)
    #    return np.nan_to_num(res)

    if kind == "value":
        norm = np.abs(val / limit)
        return np.nan_to_num(np.where(norm > 1, norm, norm**b) * limit * np.sign(val))
    elif kind == "deviation":
        diff = np.insert(np.diff(val), 0, 0.0, axis=0)
        norm = np.abs(diff / limit)

        res = np.where(norm > 1, norm, norm**b) * limit * np.sign(diff)

        smoothed = res.cumsum()
        return np.nan_to_num(smoothed - np.mean(smoothed) + np.mean(val))
    else:
        raise ValueError(f"kind {kind} not recognized")
