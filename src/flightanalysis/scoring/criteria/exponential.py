from __future__ import annotations
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from flightanalysis.base.utils import parse_csv


@dataclass
class Exponential:
    factor: float
    exponent: float
    limit: float | None = None

    def __call__(self, value):
        val = self.factor * value**self.exponent
        return val # np.minimum(val, self.limit) if self.limit and limits else val

    def __eq__(self, other):
        if not isinstance(other, Exponential):
            return False
        return (
            np.isclose(self.factor, other.factor)
            and np.isclose(self.exponent, other.exponent)
            and (
                self.limit == other.limit
                or (self.limit and other.limit and np.isclose(self.limit, other.limit))
            )
        )

    def to_simple(self):
        return (
            self.exponent,
            self.error_limit,
            self.limit
        )   

    @staticmethod
    def simple(exponent: float, error: float, downgrade: float, has_limit: bool = True):
        return Exponential(
            downgrade / error**exponent, exponent, downgrade# if has_limit else None
        )

    @property
    def error_limit(self):
        if self.limit is None or self.factor == 0:
            return 1.0
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

        x = np.linspace(0, self.error_limit * 1.2, 30)
        return go.Scatter(
            x=x, y=self(x), name=f"{self.factor} * x^{self.exponent}", **kwargs
        )

    def plot(self):
        import plotly.graph_objects as go

        fig = go.Figure(
            [self.trace()],
            layout=dict(xaxis=dict(title="error"), yaxis=dict(title="downgrade")),
        )

        return fig


free = Exponential(0, 1)


def parse_expos_from_csv(file: Path | str):
    df = parse_csv(file, sep=";")

    expos: dict[str, dict[str, Exponential]] = {}
    for grpname, grp in df.groupby("group"):
        expos[grpname] = {}
        for row in grp.itertuples(index=False):
            expos[grpname][row.name] = Exponential.simple(
                row.exponent,
                row.error,
                row.downgrade,
                row.haslimit,
            )
    return namedtuple("Expos", expos.keys())(
        *[namedtuple(k, v.keys())(**v) for k, v in expos.items()]
    )