from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from flightdata.base import to_list
from flightanalysis.scoring.measurement import Measurement
from flightanalysis.scoring.criteria import Criteria
from dataclasses import dataclass, replace
from geometry.utils import get_value


def diff(val, factor=3):
    """factor == 1 (easy), 2 (medium), 3 (hard)"""
    b = 1.3 - factor * 0.1
    m = 6 / 6**b
    try:
        with np.errstate(invalid="raise"):
            return m * val**b
    except FloatingPointError:
        pass

def trunc(val):
    return np.floor(val * 2) / 2


@dataclass
class Result:
    """
    Intra - this Result covers the downgrades applicable to things like the change of radius within an element.
    Inter - This result would cover the downgrades applicable to a set of loop diameters within a manoevre (one ManParm)
    """

    name: str
    measurement: Measurement  # the raw measured data
    visibility: npt.NDArray  # the visibility of the error
    sample: npt.NDArray  # the selected, visibility weighted sample used for scoring
    sample_keys: npt.NDArray  # the keys to link the sample to the measurement
    errors: npt.NDArray  # the errors resulting from the comparison
    dgs: npt.NDArray  # downgrades for the errors
    keys: npt.NDArray  # links from dgs to sample index
    criteria: Criteria
    meta: dict = None  # extra info about the score calculation

    @property
    def total(self):
        return float(sum(self.dgs))

    def score(self, difficulty=3, truncate: None | str = None):
        res = sum(diff(self.dgs, difficulty))
        return trunc(res) if truncate == "result" else res

    def replace_criteria(self, new_criteria: Criteria, limits: bool=True):
        mistakes, dgs, keys = new_criteria(self.sample, limits)
        return replace(
            self,
            errors=mistakes,
            dgs=dgs,
            keys=keys,
            criteria=new_criteria
        )

    def replace_lookup(self, new_lookup, limits: bool=True):
        new_criteria = replace(self.criteria, lookup=new_lookup)
        return self.replace_criteria(new_criteria, limits=limits)

    def to_dict(self):
        return dict(
            name=self.name,
            measurement=self.measurement.to_dict(),
            visibility=to_list(self.visibility),
            sample=to_list(self.sample),
            sample_keys=to_list(self.sample_keys),
            errors=to_list(self.errors),
            dgs=to_list(self.dgs),
            keys=to_list(self.keys),
            total=self.total,
            criteria=self.criteria.to_dict(),
            meta=self.meta,
        )

    def __repr__(self):
        return f"Result({self.name}, {self.total:.3f})"

    @staticmethod
    def from_dict(data) -> Result:
        return Result(
            data["name"],
            np.array(data["measurement"]),
            np.array(data["visibility"]),
            np.array(data["sample"]),
            np.array(data["sample_keys"]),
            np.array(data["errors"]),
            np.array(data["dgs"]),
            np.array(data["keys"]),
            Criteria.from_dict(data["criteria"]),
            data.get("meta", None),
        )

    def info(self, i: int):
        dgkey = self.keys[i]
        mkey = self.sample_keys[dgkey]
        return "\n".join(
            [
                f"dg={self.dgs[i]:.3f}",
                # f"meas={self.plot_f(self.measurement.value[mkey]):.2f}",
                # f"vis={self.measurement.visibility[mkey]:.2f}",
                f"sample={self.plot_f(self.sample[dgkey]):.2f}",
                f"err={self.plot_f(self.errors[i]):.2f}",
            ]
        )

    def summary_df(self):
        return pd.DataFrame(
            np.column_stack(
                [
                    self.keys,
                    self.visibility,
                    self.measurement,
                    self.sample,
                    self.errors,
                    self.dgs,
                ]
            ),
            columns=[
                "collector",
                "visibility",
                "measurement",
                "sample",
                "error",
                "downgrade",
            ],
        )

    def inter_df(self):
        data = []
        for i in range(len(self.measurement)):
            data.append(dict(
                name=f"{i+1}",
                measurement=self.measurement[i],
                error = self.errors[i] + 1,
                visibility = self.visibility[i],
                downgrade = self.dgs[i],
            ))
        return pd.DataFrame(data).T

    @property
    def plot_f(self):
        return np.degrees if self.measurement.unit.find("rad") >= 0 else lambda x: x
    

    def measurement_trace(self, xvs=None, **kwargs):
        import plotly.graph_objects as go

        x = self.sample_keys if xvs is None else xvs
        return [
            go.Scatter(
                **(
                    dict(
                        x=x,
                        y=self.plot_f(self.measurement),
                        name="Measurement",
                        mode="lines",
                        **kwargs,
                        line=dict(color="blue", width=1, dash="dash"),
                    )
                    | kwargs
                )
            ),
            *(
                [
                    go.Scatter(
                        **(
                            dict(
                                x=x,
                                y=self.plot_f(self.measurement)[self.sample_keys],
                                mode="lines",
                                name="Selected",
                                line=dict(color="blue", width=1, dash="solid"),
                            )
                            | kwargs
                        )
                    )
                ]
                if not len(self.sample) == len(self.measurement)
                else []
            ),
        ]

    def sample_trace(self, xvs=None, **kwargs):
        import plotly.graph_objects as go

        return [
            go.Scatter(
                **(
                    dict(
                        x=self.sample_keys if xvs is None else xvs,
                        y=self.plot_f(self.sample),
                        mode="lines",
                        name="Smooth Sample",
                        line=dict(width=1, color="black"),
                    )
                    | kwargs
                )
            ),
        ]

    def downgrade_trace(self, xvs=None, **kwargs):
        import plotly.graph_objects as go

        if len(self.keys) == 0:
            return go.Scatter()
        return go.Scatter(
            **(
                dict(
                    x=self.sample_keys[self.keys] if xvs is None else xvs[self.keys],
                    y=self.plot_f(self.sample[self.keys]),
                    text=np.round(self.dgs, 3),
                    hovertext=[self.info(i) for i in range(len(self.keys))],
                    mode="markers+text",
                    name="Downgrades",
                    textposition="bottom right",
                    yaxis="y",
                    marker=dict(size=10, color="black"),
                )
                | kwargs
            )
        )

    def visibility_trace(self, xvs=None, **kwargs):
        import plotly.graph_objects as go

        return go.Scatter(
            **(
                dict(
                    x=self.sample_keys if xvs is None else xvs,
                    y=self.visibility,
                    mode="lines",
                    name="Visibility",
                    yaxis="y2",
                    line=dict(width=1, color="black", dash="dot"),
                )
                | kwargs
            )
        )

    def traces(self, xvals: np.ndarray = None, **kwargs):
        return [
            *self.measurement_trace(xvals, **kwargs),
            *self.sample_trace(xvals, **kwargs),
            self.downgrade_trace(xvals, **kwargs),
            self.visibility_trace(xvals, **kwargs),
        ]

    def plot(self, xvals: np.ndarray = None):
        import plotly.graph_objects as go
        xtitle = "Time (s)" if xvals is not None else "Index"
        xvals = np.arange(np.ceil(self.sample_keys[-1]+1)) if xvals is None else xvals

        fig = go.Figure(
            layout=dict(
                yaxis2=dict(
                    title="Visibility", overlaying="y", range=[0, 1], side="right"
                ),
                title=f"{self.name}, {self.total:.2f}",
                legend=dict(orientation="h", x=0, y=1.4, yanchor="top"),
                margin=dict(t=10, r=90, b=90, l=90),
                xaxis=dict(visible=True, title=xtitle, range=[0, xvals[-1]]),
                yaxis=dict(title=f"Measurement ({self.measurement.unit.replace("rad", "degrees")})"),
            ),
            data=self.traces(np.array(get_value(xvals, self.sample_keys))),
        )

        return fig


def comparison_plot(r1: Result | None, r2: Result | None):
    from plotly.subplots import make_subplots

    fig = make_subplots(
        1,
        2,
        column_widths=[0.5, 0.5],
        specs=[
            [
                {"secondary_y": True},
                {"secondary_y": True},
            ]
        ],
        horizontal_spacing=0.05,
    )
    if r1 is not None:
        d = r1.plot().data
        fig.add_traces(d[:-1], rows=[1] * (len(d) - 1), cols=[1] * (len(d) - 1))
        fig.add_trace(d[-1], row=1, col=1, secondary_y=True)
    if r2 is not None:
        d = r2.plot().data
        fig.add_traces(d[:-1], rows=[1] * (len(d) - 1), cols=[2] * (len(d) - 1))
        fig.add_trace(d[-1], row=1, col=2, secondary_y=True)
    fig.update_layout(
        title=f"{r1.name if r1 is not None else r2.name}, L={(r1.total if r1 else 0):.4f}, R={r2.total if r2 else 0:.4f}",
        yaxis=dict(title="Roll Rate", range=[0, 2]),
        yaxis2=dict(range=[0, 1]),
        yaxis3=dict(range=[0, 2]),
        yaxis4=dict(title="Visibility", range=[0, 1]),
        # xaxis=dict(range=[0, len(fl1)]),
        # xaxis2=dict(range=[0, len(fl2)]),
        margin=dict(l=0, r=0, t=30, b=0),
        height=300,
    )
    for tr in fig.data:
        tr.showlegend = False
    return fig
