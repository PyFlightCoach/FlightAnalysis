from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from flightdata import Collection
from flightdata.base import to_list
from flightanalysis.scoring.measurements.measurement import Measurement
from flightanalysis.scoring.criteria import Criteria
from dataclasses import dataclass


def ease(val, factor=3):
    """factor == 3 for hard / no easement"""
    with np.errstate(invalid="raise"):
        b = 1.3 - factor * 0.1
        m = 6 / 6**b
        return m * val**b


def trunc(val):
    return np.floor(val * 2) / 2


@dataclass
class Result:
    """
    Intra - this Result covers the downgrades applicable to things like the change of radius within an element.
    Inter - This result covers the downgrades applicable to a set of loop diameters within a manoevre (one ManParm)
    """

    name: str
    measurement: Measurement  # the raw measured data
    sample: npt.NDArray  # the smoothed & downselected data
    sample_keys: npt.NDArray  # the keys to link the sample to the measurement
    errors: npt.NDArray  # the errors resulting from the comparison
    dgs: npt.NDArray  # downgrades for the errors
    keys: npt.NDArray  # links from dgs to sample index
    criteria: Criteria

    @property
    def total(self):
        return float(sum(self.dgs))

    def score(self, difficulty=3, truncate: None | str = None):
        res = sum(ease(self.dgs, difficulty))
        return trunc(res) if truncate == "result" else res

    def to_dict(self):
        return dict(
            name=self.name,
            measurement=self.measurement.to_dict()
            if isinstance(self.measurement, Measurement)
            else list(self.measurement),
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
                f"meas={self.plot_f(self.measurement.value[self.sample_keys[self.keys[i]]]):.2f}",
                f"vis={self.measurement.visibility[self.sample_keys[self.keys[i]]]:.2f}",
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
                    self.sample,
                    self.errors,
                    self.dgs,
                ]
            ),
            columns=["collector", "visibility", "value", "error", "downgrade"],
        )

    @property
    def plot_f(self):
        return np.degrees if self.measurement.unit == "rad" else lambda x: x

    def measurement_trace(self, **kwargs):
        import plotly.graph_objects as go

        return [
            go.Scatter(
                x=np.arange(len(self.measurement)) / 25,
                y=self.plot_f(self.measurement.value),
                name="value",
                **kwargs,
                line=dict(color="blue", width=1, dash="dash"),
            ),
            go.Scatter(
                x=np.arange(len(self.measurement))[self.sample_keys] / 25,
                y=self.plot_f(self.measurement.value)[self.sample_keys],
                name="selected",
                line=dict(color="blue", width=1, dash="solid"),
                **kwargs,
            ),
        ]

    def sample_trace(self, **kwargs):
        import plotly.graph_objects as go

        return go.Scatter(
            x=np.arange(len(self.measurement))[self.sample_keys] / 25,
            y=self.plot_f(self.sample),
            name="sample",
            line=dict(width=1, color="black"),
            **kwargs,
        )

    def downgrade_trace(self, **kwargs):
        import plotly.graph_objects as go

        return go.Scatter(
            x=np.arange(len(self.measurement))[self.sample_keys[self.keys]] / 25,
            y=self.plot_f(self.sample[self.keys]),
            text=np.round(self.dgs, 3),
            hovertext=[self.info(i) for i in range(len(self.keys))],
            mode="markers+text",
            name="downgrade",
            textposition="bottom right",
            yaxis="y",
            marker=dict(size=10, color='black'),#, color=self.dgs, colorscale="Bluered"),
            **kwargs,
        )

    def visibility_trace(self, **kwargs):
        import plotly.graph_objects as go

        return go.Scatter(
            x=np.arange(len(self.measurement)) / 25,
            y=self.measurement.visibility,
            name="visibility",
            yaxis="y2",
            line=dict(width=1, color="black", dash="dot"),
            **kwargs,
        )

    def traces(self, **kwargs):
        return [
            *self.measurement_trace(**kwargs),
            self.visibility_trace(**kwargs),
            self.sample_trace(**kwargs),
            self.downgrade_trace(**kwargs),
        ]

    def plot(self):
        import plotly.graph_objects as go

        fig = go.Figure(
            layout=dict(
                yaxis=dict(title="measurement"),
                yaxis2=dict(
                    title="visibility", overlaying="y", range=[0, 1], side="right"
                ),
                title=f"{self.name}, {self.total:.2f}",
            ),
            data=self.traces(),
        )

        return fig


class Results(Collection):
    """
    Intra - the Results collection covers all the downgrades in one element
    Inter - the Results collection covers all the downgrades in one Manoeuvre
    """

    VType = Result
    uid = "name"

    def score(self, difficulty=3, truncate: None | str = False):
        res = sum([r.score(difficulty, truncate) for r in self])
        return trunc(res) if truncate == "results" else res

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def __repr__(self):
        return f'Results({self.name}, {self.total:.2f}, ({",".join([f"{res.total:.2f}" for res in self])}))'

    @property
    def total(self):
        return sum([cr.total for cr in self])

    def downgrade_summary(self):
        return {r.name: r.dgs for r in self if len(r.dgs) > 0}

    def downgrade_df(self) -> pd.DataFrame:
        dgs = self.downgrade_summary()
        if len(dgs) == 0:
            return pd.DataFrame()
        max_len = max([len(v) for v in dgs.values()])

        def extend(vals):
            return [vals[i] if i < len(vals) else np.NaN for i in range(max_len)]

        df = pd.DataFrame.from_dict({k: extend(v) for k, v in dgs.items()})

        return df

    def to_dict(self) -> dict[str, dict]:
        return dict(
            name=self.name,
            data={k: v.to_dict() for k, v in self.data.items()},
            total=self.total,
        )

    @staticmethod
    def from_dict(data) -> Results:
        return Results(
            data["name"], [Result.from_dict(v) for v in data["data"].values()]
        )

    def plot(self):
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=len(self),
            cols=1,
            shared_xaxes=True,
            specs=[[{"secondary_y": True}] for _ in self],
            vertical_spacing=0.03,
        )

        for i, res in enumerate(self, 1):
            fig.add_traces(res.measurement_trace(showlegend=i == 1), rows=i, cols=1)
            fig.add_trace(res.sample_trace(showlegend=i == 1), row=i, col=1)
            fig.add_trace(res.downgrade_trace(showlegend=i == 1), row=i, col=1)
            fig.add_trace(
                res.visibility_trace(showlegend=i == 1), secondary_y=True, row=i, col=1
            )

            fig.update_layout(
                **{
                    f"yaxis{i*2-1}": dict(
                        title=f'{res.name}, {res.measurement.unit.replace("rad", "deg")}',
                        rangemode='tozero',
                    ),
                    f"yaxis{i*2}": dict(
                        title='visibility',
                        range=[0, 1],
                        showgrid=False
                    ),
                },
                hovermode="x unified",
                hoversubplots="axis",
                title=f"{self.name}, {self.total:.2f}",
            )

        return fig


class ElementsResults(Collection):
    """Intra Only
    Elements Results covers all the elements in a manoeuvre
    """

    VType = Results
    uid = "name"

    def __repr__(self):
        return f"ElementsResults, total = {self.total:.2f}, \n {super().__repr__()}"

    def score(self, difficulty=3, truncate=False):
        return sum([r.score(difficulty, truncate) for r in self])

    @property
    def total(self):
        return sum([r.total for r in self])

    @property
    def downgrade_list(self):
        return [r.total for r in self]

    def downgrade_df(self):
        df = pd.concat([idg.downgrade_df().sum() for idg in self], axis=1).T
        df = pd.concat([df, pd.DataFrame(df.sum()).T])  # (np.floor(df.sum())).T])
        df.index = list(self.data.keys()) + ["Total"]

        return df

    def to_dict(self) -> dict[str, dict]:
        return dict(
            data={k: v.to_dict() for k, v in self.data.items()},
            summary=self.downgrade_list,
            total=float(self.total),
        )

    @staticmethod
    def from_dict(data) -> Results:
        return ElementsResults(
            {k: Results.from_dict(v) for k, v in data["data"].items()}
        )


@dataclass
class ManoeuvreResults:
    inter: Results
    intra: ElementsResults
    positioning: Results

    def summary(self):
        return {k: v.total for k, v in self.__dict__.items() if v is not None}

    def score_summary(self, difficulty, truncate):
        intra = self.intra.score(difficulty, "results" if truncate else None)
        inter = self.inter.score(difficulty, "result" if truncate else None)
        positioning = self.positioning.score(difficulty, "result" if truncate else None)
        return dict(
            intra=intra,
            inter=inter,
            positioning=positioning,
            total=max(10 - intra - inter - positioning, 0),
        )

    def score(self, difficulty=3, truncate: bool = False):
        return self.score_summary(difficulty, truncate)["total"]

    def to_dict(self):
        return dict(
            inter=self.inter.to_dict(),
            intra=self.intra.to_dict(),
            positioning=self.positioning.to_dict(),
            summary=self.summary(),
            score=self.score(),
        )

    @staticmethod
    def from_dict(data):
        return ManoeuvreResults(
            Results.from_dict(data["inter"]),
            ElementsResults.from_dict(data["intra"]),
            Results.from_dict(data["positioning"]),
        )

    def fcj_results(self):
        res = []
        for diff in [1, 2, 3]:
            for trunc in [False, True]:
                res.append(
                    dict(
                        score=self.score_summary(diff, trunc),
                        properties=dict(difficulty=diff, truncate=trunc),
                    )
                )
        return res
