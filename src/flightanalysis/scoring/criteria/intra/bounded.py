from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass


@dataclass
class Bounded(Criteria):
    """The bounded criteria downgrades for regions outside of bounds.
    A single downgrade is applied for each group of values outside the bounds.
    The ids correspond to the middle value in each group.
    The downgrade is the average distance from the bound multiplied by the ratio
    of the group width to the total width and by the average visibility of the group.
    """

    min_bound: float = None  # values below the min bound will be downgraded
    max_bound: float = None  # values above the max bound will be downgraded

    def __call__(self, vs: npt.NDArray, limits=True):
        """each downgrade corresponds to a group of values outside the bounds, ids
        correspond to the last value in each case"""
        # sample = self.prepare(vs)

        groups = np.concatenate([[0], np.diff(vs != 0).cumsum()])
        dgids = np.append(
            np.arange(len(groups))[1:][np.diff(groups).astype(bool)], len(groups) - 1
        )

        errors = np.array(
            [
                np.mean(vs[groups == grp]) * len(vs[groups == grp]) / len(vs)
                for grp in set(groups)
            ]
        )
        dgs = self.lookup(np.abs(errors), limits)

        return errors[dgs>0], dgs[dgs>0], dgids[dgs>0]

    def prepare(self, data: npt.NDArray):
        """prepare the sample for"""
        oarr = np.zeros_like(data)
        # below_min = np.maximum(self.min_bound - data, 0) if self.min_bound is not None else np.zeros_like(data)
        # above_max = np.maximum(data - self.max_bound, 0) if self.max_bound is not None else np.zeros_like(data)

        if self.min_bound is None and self.max_bound is None:
            raise Exception("Bounds not set.")
        elif (
            self.min_bound is not None
            and self.max_bound is not None
            and self.min_bound >= self.max_bound
        ):  # Downgrade values inside the bound.:
            midbound = (self.max_bound + self.min_bound) / 2
            b1fail = (data > midbound) & (data < self.min_bound)
            b0fail = (data <= midbound) & (data > self.max_bound)
            oarr[b1fail] = self.max_bound - data[b1fail]
            oarr[b0fail] = data[b0fail] - self.max_bound
        else:
            if self.min_bound is not None:  # downgrade below the min bound
                oarr[data < self.min_bound] = (
                    self.min_bound - data[data < self.min_bound]
                )

            if self.max_bound is not None:  # downgrade above the max bound
                oarr[data > self.max_bound] = (
                    data[data > self.max_bound] - self.max_bound
                )

        return oarr
