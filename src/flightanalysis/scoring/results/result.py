from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from flightdata.base import to_list
from flightanalysis.scoring.measurement import Measurement
from flightanalysis.scoring.criteria import Criteria
from dataclasses import dataclass


def diff(val, factor=3):
    """factor == 1 (easy), 2 (medium), 3 (hard)"""
    b = 1.3 - factor * 0.1
    m = 6 / 6**b
    return m * val**b


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
    raw_sample: npt.NDArray | None  # the visibility factored data
    sample: npt.NDArray  # the smoothed data
    sample_keys: npt.NDArray  # the keys to link the sample to the measurement
    errors: npt.NDArray  # the errors resulting from the comparison
    dgs: npt.NDArray  # downgrades for the errors
    keys: npt.NDArray  # links from dgs to sample index
    criteria: Criteria

    @property
    def total(self):
        return float(sum(self.dgs))

    def score(self, difficulty=3, truncate: None | str = None):
        res = sum(diff(self.dgs, difficulty))
        return trunc(res) if truncate == "result" else res

    def to_dict(self):
        return dict(
            name=self.name,
            measurement=self.measurement.to_dict(),
            raw_sample=to_list(self.raw_sample),
            sample=to_list(self.sample),
            sample_keys=to_list(self.sample_keys),
            errors=to_list(self.errors),
            dgs=to_list(self.dgs),
            keys=to_list(self.keys),
            total=self.total,
            criteria=self.criteria.to_dict(),
        )

    def __repr__(self):
        return f"Result({self.name}, {self.total:.3f})"

    @staticmethod
    def from_dict(data) -> Result:
        return Result(
            data["name"],
            Measurement.from_dict(data["measurement"])
            if isinstance(data["measurement"], dict)
            else np.array(data["measurement"]),
            np.array(data["raw_sample"]) if "raw_sample" in data else None,
            np.array(data["sample"]),
            np.array(data["sample_keys"]),
            np.array(data["errors"]),
            np.array(data["dgs"]),
            np.array(data["keys"]),
            Criteria.from_dict(data["criteria"]),
        )

    def info(self, i: int):
        return "\n".join(
            [
                f"dg={self.dgs[i]:.3f}",
                # f"meas={self.plot_f(self.measurement.value[self.sample_keys[self.keys[i]]]):.2f}",
                # f"vis={self.measurement.visibility[self.sample_keys[self.keys[i]]]:.2f}",
                f"sample={self.plot_f(self.sample[self.keys[i]]):.2f}",
                f"err={self.plot_f(self.errors[i]):.2f}",
            ]
        )

    def summary_df(self):
        return pd.DataFrame(
            np.column_stack(
                [
                    self.keys,
                    self.measurement.visibility,
                    self.measurement.value,
                    self.raw_sample,
                    self.sample,
                    self.errors,
                    self.dgs,
                ]
            ),
            columns=[
                "collector",
                "visibility",
                "measurement",
                "raw_sample",
                "sample",
                "error",
                "downgrade",
            ],
        )

    @property
    def plot_f(self):
        return np.degrees if self.measurement.unit == "rad" else lambda x: x

    def measurement_trace(self, xvs=None, **kwargs):
        import plotly.graph_objects as go

        return [
            go.Scatter(
                **(
                    dict(
                        x=self.sample_keys if xvs is None else xvs,
                        y=self.plot_f(self.measurement.value),
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
                                x=self.sample_keys if xvs is None else xvs,
                                y=self.plot_f(self.measurement.value)[self.sample_keys],
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
            *(
                [
                    go.Scatter(
                        **(
                            dict(
                                x=self.sample_keys if xvs is None else xvs,
                                y=self.plot_f(self.raw_sample),
                                mode="lines",
                                name="Visible Sample",
                                line=dict(width=1, color="black", dash="dash"),
                            )
                            | kwargs
                        )
                    )
                ]
                if self.raw_sample is not None
                else []
            ),
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
                    y=self.measurement.visibility,
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
            self.visibility_trace(xvals, **kwargs),
            *self.sample_trace(xvals, **kwargs),
            self.downgrade_trace(xvals, **kwargs),
        ]

    def plot(self, xvals: np.ndarray = None):
        import plotly.graph_objects as go

        fig = go.Figure(
            layout=dict(
                yaxis=dict(title="measurement"),
                yaxis2=dict(
                    title="visibility", overlaying="y", range=[0, 1], side="right"
                ),
                title=f"{self.name}, {self.total:.2f}",
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.0,
                    xanchor="left",
                    x=0.3,
                    bgcolor="rgba(0,0,0,0)",
                ),
            ),
            data=self.traces(xvals),
        )

        return fig
