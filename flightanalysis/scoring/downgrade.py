
from flightdata import Collection, State
from .criteria import Single, Continuous, Criteria
from .measurement import Measurement
from .results import Results, Result
from typing import Callable 
from geometry import Coord
from dataclasses import dataclass
import numpy as np
import pandas as pd

from scipy.signal import butter, filtfilt


def butter_filter(data, cutoff):
    return filtfilt(*butter(2, cutoff / 15, btype='low', analog=False), data)

def convolve(data, width):
    kernel = np.ones(width) / width
    l = len(data)
    outd = np.full(l, np.nan)
    conv = np.convolve(data, kernel, mode='valid')
    ld = (len(data) - len(conv))/2
    outd[int(np.ceil(ld)):-int(np.floor(ld))] = conv
    return pd.Series(outd).ffill().bfill().to_numpy()


def remove_outliers(data, nstds = 1):
    std = np.nanstd(data)
    mean = np.nanmean(data)
    data = data.copy()

    data[abs(data - mean) > nstds * std] = np.nan

    return pd.Series(data).ffill().bfill().to_numpy()



@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
        measure - a Measurement constructor
        criteria - takes a Measurement and calculates the score
    """
    measure: Callable[[State, State, Coord], Measurement]
    criteria: Criteria

    def to_dict(self):
        return dict(
            measure=self.measure.__name__,
            criteria=self.criteria.to_dict()
        )

    @property
    def name(self):
        return self.measure.__name__
    
    def __call__(self, fl, tp, coord) -> Result:
        # TODO this needs to check the element before and after. If there is a step change (for example loop radius) then the 
        #ends should be cut off. If not (for example track or roll angle) the ends should not be cut off
        if isinstance(self.criteria, Single):
            measurement = self.measure(fl[-1], tp[-1], coord)
            vals = self.criteria.prepare(measurement.value, measurement.expected)    

            id, error, dg = self.criteria([0], vals)
            dg = dg * measurement.visibility[id]
        elif isinstance(self.criteria, Continuous):
            measurement = self.measure(fl, tp, coord)

            if self.criteria.comparison == 'ratio':
                if len(measurement) < 30:
                    return Result(self.measure.__name__, measurement, [0], [0], [0], [0])

                endcut = 4 #min(3, int((len(vals) - 5) / 2))
                vals = np.abs(remove_outliers(measurement.value))
                tempvals = np.full(len(fl), np.mean(vals))
                tempvals[endcut:-endcut] = vals[endcut:-endcut]
                tempvals = convolve(pd.Series(tempvals).ffill().bfill().to_numpy(), 20)
            else:
                tempvals = measurement.value - measurement.expected

            id, error, dg = self.criteria(
                list(range(len(fl))),
                abs(tempvals)
            )
            vals = tempvals

            #visiblity factors are now applied to the downgrades for absolute and ratio errrors, 
            # so if the initial error happened when it was hard to see then you don't
            #  get downgraded further as it becomes more apparant. 
            rids = np.concatenate([[0], id])
            vis = np.array([np.mean(measurement.visibility[a:b]) for a, b in zip(rids[:-1], rids[1:])])
            dg = vis * dg
        else:
            raise TypeError(f'Expected a Criteria, got {self.criteria.__class__.__name__}')
        
        return Result(self.measure.__name__, measurement, vals, error, dg, id)


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, coord) -> Results:
        return Results(el.uid, [dg(fl, tp, coord) for dg in self])
       