import numpy as np
import pandas as pd
from typing import Literal

def apply_visibility(val, factor: float, limit: float, kind: Literal["deviation", "value"] = 'value'):
    """factor between 0 and 1"""

    b = 2.2 - factor * 1.2
    if kind == 'value':
        norm = np.abs(val / limit)
        return np.where(norm > 1, norm, norm**b) * limit * np.sign(val)
    elif kind=='deviation':
        diff = np.insert(np.diff(val), 0, 0.0, axis=0)
        norm = np.abs(diff / limit)

        res = np.where(norm > 1, norm, norm**b) * limit * np.sign(diff) 
        return res.cumsum() + val[0]
    else:
        raise ValueError(f'kind {kind} not recognized')


