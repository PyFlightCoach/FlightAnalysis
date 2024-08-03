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
    def prepare(self, value: npt.NDArray, expected: float) -> npt.NDArray:
        return abs(value - expected)
             
    def __call__(self, name: str, m: Measurement, sids: npt.NDArray, limits=True) -> Result:
        
        sample = self.prepare(m.value[sids], m.expected)
                
        return Result(
            name, m, sample, sids, sample,
            self.lookup(sample, m.visibility, limits),
            np.arange(len(sample))
        )
        

class SingRat(Single):    
    def prepare(self, value: NDArray, expected: float):
        ae = abs(expected)
        af = abs(value)
        return np.maximum(af,ae) / np.minimum(af,ae)