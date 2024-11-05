from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class Exponential:
    factor: float
    exponent: float
    limit: float | None = None

    def __call__(self, value, limits=True):
        val = self.factor * value**self.exponent
        return np.minimum(val, self.limit) if self.limit and limits else val

    @property
    def error_limit(self):
        return (self.limit / self.factor) ** (1 / self.exponent)

    @staticmethod
    def linear(factor: float):
        return Exponential(factor, 1)

    @staticmethod
    def fit_points(xs, ys, limit=None):
        from scipy.optimize import curve_fit

        res = curve_fit(lambda x, factor, exponent: factor * x**exponent, xs, ys)
        assert np.all(np.isreal(res[0]))
        return Exponential(res[0][0], res[0][1], limit)

    def trace(self, **kwargs):
        import plotly.graph_objects as go

        x = np.linspace(0, self.error_limit*1.2, 30)
        return go.Scatter(
            x=x, y=self(x), name=f"{self.factor} * x^{self.exponent}", **kwargs
        )

    def plot(self):
        import plotly.graph_objects as go

        fig = go.Figure(
            [self.trace()], 
            layout=dict(xaxis=dict(title="error"), yaxis=dict(title="downgrade"))
        )

        return fig


free = Exponential(0, 1)
