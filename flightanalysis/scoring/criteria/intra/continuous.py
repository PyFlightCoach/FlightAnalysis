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
        last_val = increasing[-1]
        first_val = not increasing[0]
        if rev:
            last_val = not last_val
            first_val = not first_val
        return np.concatenate([np.array([first_val]), peaks, np.array([last_val])])

    def __call__(self, name: str, m: Measurement, limits=True) -> Result:
        sample = self.prepare(m.value, m.expected)
        peak_locs = Continuous.get_peak_locs(sample)
        trough_locs = Continuous.get_peak_locs(sample, True)
        mistakes = self.__class__.mistakes(sample, peak_locs, trough_locs)
        dgids = self.__class__.dgids(
            np.linspace(0, len(sample)-1, len(sample)).astype(int), 
            peak_locs, trough_locs
        )

        return Result(
            name, m, sample, mistakes, 
            self.lookup(mistakes, self.visibility(m, dgids), limits), 
            dgids
        )
        
    
    def visibility(self, measurement, ids):
        rids = np.concatenate([[0], ids])
        return np.array([np.mean(measurement.visibility[a:b]) for a, b in zip(rids[:-1], rids[1:])])

    @staticmethod
    def convolve(data, width):
        kernel = np.ones(width) / width
        outd = np.full(len(data), np.nan)
        conv = np.convolve(data, kernel, mode='valid')
        ld = (len(data) - len(conv))/2
        ldc = int(np.ceil(ld))
        ldf = int(np.floor(ld))
        outd[ldf:-ldc] = conv
        outd[:ldf] = np.linspace(np.mean(data[:ldf]), conv[0],ldf+1)[:-1]
        outd[-ldc:] = np.linspace(conv[-1], np.mean(data[-ldc:]), ldc+1)[1:]
        return outd
    
    @staticmethod
    def convolve_wind(data, window_ratio, max_window):
        window = min(len(data)//window_ratio, max_window)
        sample = Continuous.convolve(data, window)
        _mean = np.mean(sample)
        sample = (sample - _mean) * window / max_window + _mean
        return sample 
    
class ContAbs(Continuous):
    def prepare(self, values: npt.NDArray, expected: float):
        sample = values - expected
        if len(sample) <= 8:
            return np.linspace(values[0],values[-1], len(sample))
        else:
            return Continuous.convolve_wind(values, 3, 40)
        
    @staticmethod
    def mistakes(data, peaks, troughs):
        '''All increases away from zero are downgraded (only peaks)'''
        last_trough = -1 if troughs[-1] else None
        first_peak = 1 if peaks[0] else 0
        return np.abs(data[first_peak:][peaks[first_peak:]] - data[:last_trough][troughs[:last_trough]])

    @staticmethod
    def dgids(ids, peaks, troughs):
        first_peak = 1 if peaks[0] else 0
        return ids[first_peak:][peaks[first_peak:]]


class ContRat(Continuous):
    
    def prepare(self, values: npt.NDArray, expected: float):
        if len(values) <= 8:
            return np.abs(np.linspace(
                np.mean(values[:1+len(values)//3]), 
                np.mean(values[-1-len(values)//3:]), 
                len(values)
            ))
        else:
            return np.abs(Continuous.convolve_wind(values, 3, 40))

    @staticmethod
    def mistakes(data, peaks, troughs):
        '''All changes are downgraded (peaks and troughs)'''
        values = data[peaks + troughs]
        return np.maximum(values[:-1], values[1:]) / np.minimum(values[:-1], values[1:]) - 1
    
    @staticmethod
    def dgids(ids, peaks, troughs):
        return ids[peaks + troughs][1:]
    
         