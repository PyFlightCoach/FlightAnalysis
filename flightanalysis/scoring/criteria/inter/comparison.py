from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass
from flightanalysis.scoring.measurement import Measurement
from flightanalysis.scoring.results import Result


@dataclass
class Comparison(Criteria):
    def __call__(self, name: str, m: Measurement):
        vals = np.abs(np.concatenate([[m.value[0]],m.value]))
        errors = np.maximum(vals[:-1], vals[1:]) / np.minimum(vals[:-1], vals[1:]) - 1

        return Result(
            name, m, m.value, 
            errors, self.lookup(errors, m.visibility), 
            m.keys
        )
