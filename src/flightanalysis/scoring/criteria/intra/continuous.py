from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

import numpy as np
import numpy.typing as npt

from .. import Criteria
from flightanalysis.base.utils import insert_zero_crossings, remove_zero_crossings, remove_zero_crossing_ids


@dataclass
class Continuous(Criteria):
    """Works on a continously changing set of values.
    only downgrades for increases (away from zero) of the value.
    treats each separate increase (peak - trough) as a new error.
    """

    def describe(self, unit: str = "") -> str:
        return "Continuous Criteria: Downgrades are assigned to each increase in the sample away from zero."

    @staticmethod
    def get_peak_locs(arr, rev=False):
        _da = np.diff(np.abs(arr))
        increasing = (np.sign(_da) > 0) & (_da != 0)
        last_downgrade = np.column_stack([increasing[:-1], increasing[1:]])
        peaks = np.sum(last_downgrade.astype(int) * [10, 1], axis=1) == (
            1 if rev else 10
        )
        last_val = increasing[-1]
        first_val = not increasing[0]
        if rev:
            last_val = not last_val
            first_val = not first_val
        return np.concatenate([np.array([first_val]), peaks, np.array([last_val])])

    def __call__(
        self, vs: npt.NDArray, **kwargs
    ) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        if len(vs) <= 1:
            return np.array([]), np.array([]), np.array([], dtype=int)

        vs, crossings = insert_zero_crossings(vs)

        vs = np.abs(vs)

        peak_locs = Continuous.get_peak_locs(vs)
        trough_locs = Continuous.get_peak_locs(vs, True)
        mistakes = self.__class__.mistakes(vs, peak_locs, trough_locs)

        dgids = self.__class__.dgids(
            np.linspace(0, len(vs) - 1, len(vs)).astype(int), peak_locs, trough_locs
        )
        dgids = remove_zero_crossing_ids(dgids, crossings)
        return mistakes, self.lookup(np.abs(mistakes)), dgids

    @staticmethod
    def mistakes(data, peaks, troughs):
        """All increases away from zero are downgraded (only peaks)"""
        last_trough = -1 if troughs[-1] else None
        first_peak = 1 if peaks[0] else 0
        return np.abs(
            data[first_peak:][peaks[first_peak:]]
            - data[:last_trough][troughs[:last_trough]]
        )

    @staticmethod
    def dgids(ids, peaks, troughs):
        first_peak = 1 if peaks[0] else 0
        return ids[first_peak:][peaks[first_peak:]]

    def local_error(
        self,
        sample: npt.NDArray,
        dt: npt.NDArray,
        direction: Literal["left", "right"],
    ):
        """Calculate the height of each point above the last trough. (below the next peak if direction==backward)
        if direction is 'left' then the local error at each point is calculated as if the sample started
        at that point, otherwise it is calculated as if the sample ended at that point.
        """

        sample, crossings = insert_zero_crossings(sample)
            
        dsample = np.diff(np.abs(sample), prepend=np.abs(sample[0]))
        # how much does the error increase in each timestep
       
            
        # cut at zero as the error cannot decrease
        error_increment = np.where(dsample > 0, dsample, 0)

        # identify discrete sections of error
        clumps = np.split(error_increment, np.argwhere(error_increment == 0).T[0])

        # get the height of each point above the last trough
        if direction == "right":
            local_error = np.concatenate([np.cumsum(clump) for clump in clumps])
        else:
            local_error = np.concatenate(
                [np.cumsum(clump[::-1])[::-1] for clump in clumps]
            )

        local_error = remove_zero_crossings(local_error, crossings)
        return local_error  # , local_dg


    def incremental_downgrade(
        self,
        local_dg: npt.NDArray,  # local_dg = self.lookup(local_error, limits),
        direction: Literal["left", "right"],
    ):
        """Calculate the total downgrade for the element if the sample ended at each point."""

        # the downgrade delta of each point
        if direction == "right":
            dg_increment = np.diff(local_dg, prepend=local_dg[0])
        else:
            dg_increment = np.diff(local_dg[::-1], prepend=local_dg[-1])[::-1]

        # downgrade deltas cant be negative ( if it is negative its because of a different clump)
        dg_increment = np.where(dg_increment > 0, dg_increment, 0)

        return (
            dg_increment.cumsum()
            if direction == "right"
            else dg_increment[::-1].cumsum()[::-1]
        )




@dataclass
class ContinuousValue(Continuous):

    def describe(self, unit: str = "") -> str:
        return "ContinuousValue Criteria: Downgrades are assigned to each change in the sample based on the size of the change."

    @staticmethod
    def mistakes(data, peaks, troughs):
        """All changes are downgraded (peaks and troughs)"""
        values = data[peaks + troughs]
        return values[1:] - values[:-1]

    @staticmethod
    def dgids(ids, peaks, troughs):
        return ids[peaks + troughs][1:]
