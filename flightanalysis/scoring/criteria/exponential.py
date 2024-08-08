from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class Exponential:
    factor: float
    exponent: float
    limit: float | None = None
    def __call__(self, value, limits=True):
        val =  self.factor * value ** self.exponent
        return np.minimum(val, self.limit) if self.limit and limits else val
    
    @staticmethod
    def linear(factor: float):
        return Exponential(factor, 1)
    
    @staticmethod
    def fit_points(xs, ys, limit=None):
        from scipy.optimize import curve_fit
        res = curve_fit(
            lambda x, factor, exponent: factor * x ** exponent,
            xs, 
            ys)
        assert np.all(np.isreal(res[0]))
        return Exponential(res[0][0], res[0][1], limit)

free = Exponential(0,1)
