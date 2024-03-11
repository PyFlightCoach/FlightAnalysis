from __future__ import annotations
import numpy as np
from numpy._typing import NDArray
import numpy.typing as npt
from dataclasses import dataclass
from .. import Criteria
from flightanalysis.scoring import Result, Measurement
from typing import Union


@dataclass
class Single(Criteria):
    id: Union[int, None] = -1
    def prepare(self, value: npt.NDArray, expected: float) -> npt.NDArray:
        return abs(value - expected)
        
    def select(self, arr: npt.NDArray) -> npt.NDArray:
        return arr if self.id is None else np.array([arr[self.id]])
     
    def __call__(self, name: str, m: Measurement) -> Result:
        
        sample = self.select(self.prepare(m.value, m.expected))
        ids = self.select(np.linspace(0, len(sample)-1, len(sample)))
        vis = self.select(m.visibility)
        
        return Result(
            name, m, sample, sample[sample!=0], 
            self.lookup(sample[sample!=0]) * vis[sample!=0],
            ids[sample!=0]
        )
        

class SingRat(Single):    
    def prepare(self, value: NDArray, expected: float):
        ae = abs(expected)
        af = abs(value)
        return np.maximum(af,ae) / np.minimum(af,ae)