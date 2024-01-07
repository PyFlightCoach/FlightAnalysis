from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass
from typing import Union
from flightanalysis.scoring import Measurement, Result

@dataclass
class Bounded(Criteria):
    bound: Union[float,list[float]] = 0

    def prepare(self, value: npt.NDArray, expected: float):
        return self.get_errors(value - expected) 
    
    def get_errors(self, ids: npt.NDArray, data: npt.NDArray):
        raise Exception("Method not available in base class")
    
    def __call__(self, name: str, m: Measurement) -> Result:
        '''each downgrade corresponds to a group of values outside the bounds, ids
        correspond to the last velue in each case'''
        sample = self.prepare(m.value, m.expected)
        ids = np.linspace(0, len(sample)-1, len(sample)).astype(int)
        groups = np.concatenate([[0], np.diff(sample!=0).cumsum()])
        
        mistakes = np.array([np.mean(sample[groups==grp]) for grp in set(groups)])
        dgids = np.array([ids[groups==grp][int(len(ids[groups==grp])/2)] for grp in set(groups)])
        dgs = np.array([self.lookup(np.mean(sample[groups==grp])) * len(sample[groups==grp]) / len(sample) for grp in set(groups)])
        
        return Result(name, m, sample, mistakes[dgs>0], dgs[dgs>0] * m.visibility[dgids[dgs>0]], dgids[dgs>0])
        
    
    def visiblity(self, measurement, ids):
        return np.mean(measurement.visibility[ids])

@dataclass    
class MaxBound(Bounded):
    def get_errors(self, data: npt.NDArray):
        oarr = np.zeros_like(data)
        oarr[data > self.bound] = data[data > self.bound] - self.bound
        return oarr
                
@dataclass
class MinBound(Bounded):
    def get_errors(self, data: npt.NDArray):
        oarr = np.zeros_like(data)
        oarr[data < self.bound] = self.bound - data[data < self.bound]
        return oarr
        

@dataclass
class OutsideBound(Bounded):
    def get_errors(self, data: npt.NDArray):
        midbound = np.mean(self.bound)
        oarr = np.zeros_like(data)
        b1fail = (data >= midbound) & (data < self.bound[1])
        b0fail = (data < midbound) & (data > self.bound[0])
        oarr[b1fail] = self.bound[1] - data[b1fail]
        oarr[b0fail] = data[b0fail] - self.bound[0]
        return oarr
                
@dataclass
class InsideBound(Bounded):
    def get_errors(self, data: npt.NDArray):
        oarr = np.zeros_like(data)
        oarr[data > self.bound[1]] = data[data > self.bound[1]] - self.bound[1]
        oarr[data < self.bound[0]] = self.bound[0] - data[data < self.bound[0]]
        return oarr
