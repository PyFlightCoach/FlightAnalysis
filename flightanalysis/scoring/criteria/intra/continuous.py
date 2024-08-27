from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Continuous(Criteria):
    """Works on a continously changing set of values.
    only downgrades for increases (away from zero) of the value.
    treats each separate increase (peak - trough) as a new error.
    """

    @staticmethod
    def get_peak_locs(arr, rev=False):
        increasing = np.sign(np.diff(np.abs(arr))) > 0
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


    def __call__(self, vs: npt.NDArray, limits=True) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        if len(vs) <= 1:
            return np.array([]), np.array([]), np.array([], dtype=int)
        
        vs = np.abs(vs)
        
        peak_locs = Continuous.get_peak_locs(vs)
        trough_locs = Continuous.get_peak_locs(vs, True)
        mistakes = self.__class__.mistakes(vs, peak_locs, trough_locs)
        dgids = self.__class__.dgids(
            np.linspace(0, len(vs) - 1, len(vs)).astype(int), peak_locs, trough_locs
        )
        return mistakes, self.lookup(np.abs(mistakes), limits), dgids

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


@dataclass
class ContinuousValue(Continuous):


    @staticmethod
    def mistakes(data, peaks, troughs):
        '''All changes are downgraded (peaks and troughs)'''
        values = data[peaks + troughs]
        return values[1:] - values[:-1]
    

    @staticmethod
    def dgids(ids, peaks, troughs):
        return ids[peaks + troughs][1:]