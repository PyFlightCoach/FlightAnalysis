import numpy as np
import pandas as pd
from typing import Literal

def apply_visibility(val, factor: float, limit: float, kind: Literal["deviation", "value"] = 'value'):
    """factor between 0 and 1"""

    with np.errstate(divide="ignore"):
        b = 1 / factor

    #res = (val / limit)**(1/factor)
#    return np.nan_to_num(res)

    if kind == 'value':
        norm = np.abs(val / limit)
        return np.nan_to_num(np.where(norm > 1, norm, norm**b) * limit * np.sign(val))
    elif kind=='deviation':
        diff = np.insert(np.diff(val), 0, 0.0, axis=0)
        norm = np.abs(diff / limit)

        res = np.where(norm > 1, norm, norm**b) * limit * np.sign(diff) 

        smoothed = res.cumsum()
        return np.nan_to_num(smoothed - np.mean(smoothed) + np.mean(val))
    else:
        raise ValueError(f'kind {kind} not recognized')


