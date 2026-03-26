from __future__ import annotations
from flightdata.state.state import State
import numpy as np
import numpy.typing as npt
import pandas as pd
from flightdata.base import to_list
from flightanalysis.scoring.measurement import Measurement
from flightanalysis.scoring.criteria import Criteria
from dataclasses import dataclass, replace


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

    def replace_criteria(self, new_criteria: Criteria, limits: bool = True):
        mistakes, dgs, keys = new_criteria(self.sample, limits)
        return replace(self, errors=mistakes, dgs=dgs, keys=keys, criteria=new_criteria)

    def replace_lookup(self, new_lookup, limits: bool = True):
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
            data.append(
                dict(
                    name=f"{i + 1}",
                    measurement=self.measurement[i],
                    error=self.errors[i] + 1,
                    visibility=self.visibility[i],
                    downgrade=self.dgs[i],
                )
            )
        return pd.DataFrame(data).T

    @property
    def plot_f(self):
        return np.degrees if self.measurement.unit.find("rad") >= 0 else lambda x: x

    def plot(self, st: State, fig=None, row=None, col=None):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        if fig is None:
            fig = make_subplots(
                rows=1, cols=1, shared_xaxes=True, specs=[[{"secondary_y": True}]]
            )
        
        sliced_st = st.iloc[self.sample_keys[0]:self.sample_keys[-1]]
        
        
        fig.add_trace(
            go.Scatter(
                x=st.t,
                y=self.measurement.value,
                mode="lines",
                name="Measurement",
                line=dict(color="blue", dash="solid"),
            ),
            row=row,
            col=col,
        )
        fig.add_trace(
            go.Scatter(
                x=st.t,
                y=self.visibility,
                mode="lines",
                name="Visibility",
                line=dict(color="blue", dash="dash"),
                yaxis="y2",
            ),
            row=row,
            col=col,
        )
        fig.add_trace(
            go.Scatter(x=sliced_st.t, y=self.sample, name="Errors"),
            row=row,
            col=col,
        )

        fig.update_yaxes(
            overlaying="y",
            side="right",
            range=[0, 1],
            secondary_y=True,
            row=row,
            col=col,
        )

        return fig
