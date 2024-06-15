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
    id: int | None = -1
    def prepare(self, value: npt.NDArray, expected: float) -> npt.NDArray:
        return abs(value - expected)
             
    def __call__(self, name: str, m: Measurement, limits=True) -> Result:
        
        sample = self.prepare(m.value, m.expected)
        all_ids = np.array(range(len(m)))
        ids = all_ids if self.id is None else np.array([all_ids[self.id]])
                
        return Result(
            name, m, sample, sample[ids], 
            self.lookup(sample[ids], m.visibility[ids], limits),
            ids
        )
        

class SingRat(Single):    
    def prepare(self, value: NDArray, expected: float):
        ae = abs(expected)
        af = abs(value)
        return np.maximum(af,ae) / np.minimum(af,ae)