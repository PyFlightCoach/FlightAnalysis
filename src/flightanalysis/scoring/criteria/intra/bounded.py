from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass
from typing import Literal
from flightanalysis.base.utils import display_unit

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
    
    def __call__(self, vs: npt.NDArray, **kwargs):
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
        dgs = self.lookup(np.abs(errors))

        return errors[dgs>0], dgs[dgs>0], dgids[dgs>0]

    def local_downgrade(
        self,
        sample: npt.NDArray,
        dt: npt.NDArray,
        direction: Literal["left", "right"],
    ):
        if direction == "right":
            return self.lookup(np.cumsum(sample) / np.arange(1, len(sample) + 1))
        else:
            return self.lookup(np.cumsum(sample[::-1])[::-1] / np.arange(len(sample), 0, -1))


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
            oarr[b1fail] = self.min_bound - data[b1fail]
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

    def short_description(self, unit: str = "") -> str:
        _bs=[]
        if self.min_bound is not None:
            _bs.append(f">={display_unit(self.min_bound, unit, 2)}")
        if self.max_bound is not None:
            _bs.append(f"<={display_unit(self.max_bound, unit, 2)}")
        return f"{self.__class__.__name__} ({', '.join(_bs)})"


    def describe(self, unit: str = "") -> str:
        region=""
        if self.min_bound is not None and self.max_bound is not None:
            if self.min_bound < self.max_bound:
                region = f"Regions of the sample below {display_unit(self.min_bound, unit, 2)}, or above {display_unit(self.max_bound, unit, 2)} are downgraded." 
            else:
                region =f"Regions of the sample between {display_unit(self.max_bound, unit, 2)} and {display_unit(self.min_bound, unit, 2)} are downgraded." 
        elif self.min_bound is not None:
            region = f"Regions of the sample below {display_unit(self.min_bound, unit, 2)} are downgraded."
        elif self.max_bound is not None:
            region = f"Regions of the sample above {display_unit(self.max_bound, unit, 2)} are downgraded."
        
        return f"{super().describe()}: {region} Downgrades are assigned to each exceedence based on the average distance from the bound(s) and the ratio of its width to the total sample width."
