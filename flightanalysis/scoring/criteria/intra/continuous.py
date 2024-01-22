from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from .. import Criteria
from dataclasses import dataclass
from flightanalysis.scoring import Measurement, Result


@dataclass
class Continuous(Criteria):
    """Works on a continously changing set of values. 
    only downgrades for increases (away from zero) of the value.
    treats each separate increase (peak - trough) as a new error.
    """
    @staticmethod
    def get_peak_locs(arr, rev=False):
        increasing = np.sign(np.diff(np.abs(arr)))>0
        last_downgrade = np.column_stack([increasing[:-1], increasing[1:]])
        peaks = np.sum(last_downgrade.astype(int) * [10,1], axis=1) == (1 if rev else 10)
        last_val = False if rev else increasing[-1]
        first_val = increasing[0] if rev else False
        return np.concatenate([np.array([first_val]), peaks, np.array([last_val])])

    def __call__(self, name: str, m: Measurement) -> Result:
        sample = self.prepare(m.value, m.expected)
        peak_locs = Continuous.get_peak_locs(sample)
        trough_locs = Continuous.get_peak_locs(sample, True)
        mistakes = self.__class__.mistakes(sample, peak_locs, trough_locs)
        dgids = self.__class__.dgids(
            np.linspace(0, len(sample)-1, len(sample)).astype(int), 
            peak_locs, trough_locs
        )
        
        return Result(name, m, sample, mistakes, self.lookup(mistakes) * self.visibility(m, dgids), dgids)
        
    
    def visibility(self, measurement, ids):
        rids = np.concatenate([[0], ids])
        return np.array([np.mean(measurement.visibility[a:b]) for a, b in zip(rids[:-1], rids[1:])])
        

class ContAbs(Continuous):
    def prepare(self, value: npt.NDArray, expected: float):
        return  value - expected

    @staticmethod
    def mistakes(data, peaks, troughs):
        '''All increases away from zero are downgraded (only peaks)'''
        return np.abs(data[peaks] - data[troughs])

    @staticmethod
    def dgids(ids, peaks, troughs):
        return ids[peaks]


class ContRat(Continuous):

    @staticmethod
    def convolve(data, width):
        kernel = np.ones(width) / width
        l = len(data)
        outd = np.full(l, np.nan)
        conv = np.convolve(data, kernel, mode='valid')
        ld = (len(data) - len(conv))/2
        outd[int(np.ceil(ld)):-int(np.floor(ld))] = conv
        return pd.Series(outd).ffill().bfill().to_numpy()
    
    def prepare(self, values: npt.NDArray, expected: float):
        endcut = 0
        window = 20
        sample = np.full(len(values), expected)
        sample[endcut:-endcut-1] = values[endcut:-endcut-1]
        sample = values
        if len(sample) <= window + endcut * 2:
            return np.full(len(sample), abs(np.mean(sample)))
        else:
            return np.abs(ContRat.convolve(sample, 20))
        
    @staticmethod
    def mistakes(data, peaks, troughs):
        '''All changes are downgraded (peaks and troughs)'''
        values = np.concatenate([[data[0]], data[peaks + troughs]])
        return np.maximum(values[:-1], values[1:]) / np.minimum(values[:-1], values[1:]) - 1
    
    @staticmethod
    def dgids(ids, peaks, troughs):
        return ids[peaks + troughs]
    
         