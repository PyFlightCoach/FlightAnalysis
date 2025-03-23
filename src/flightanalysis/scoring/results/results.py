from __future__ import annotations
import numpy as np
import pandas as pd
from flightdata import Collection
from .result import Result, trunc



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

    def dg_dict(self):
        return {k: v.total for k, v in self.items()}

    def downgrade_df(self) -> pd.DataFrame:
        dgs = self.downgrade_summary()
        if len(dgs) == 0:
            return pd.DataFrame()
        max_len = max([len(v) for v in dgs.values()])

        def extend(vals):
            return [vals[i] if i < len(vals) else np.nan for i in range(max_len)]

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
                        rangemode="tozero",
                    ),
                    f"yaxis{i*2}": dict(
                        title="visibility", range=[0, 1], showgrid=False
                    ),
                },
                hovermode="x unified",
                hoversubplots="axis",
                title=f"{self.name}, {self.total:.2f}",
            )

        return fig

    def inter_dg_list(self, cutoff=0.05):
        inter_dgs = {}
        for res in self:
            for i, dg in enumerate(res.dgs):
                inter_dgs[tuple(res.measurement.keys[i].split("."))] = float(dg)
        inter_dgs = pd.Series(inter_dgs).sort_values(ascending=False)

        return inter_dgs.loc[inter_dgs > cutoff]
