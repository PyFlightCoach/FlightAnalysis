from __future__ import annotations

import numpy as np

from flightanalysis.scoring.results import Results, Result
from flightdata import State
from typing import Self
from flightanalysis import ElDef, Element, ManParms
from dataclasses import dataclass
import geometry as g


@dataclass
class ElementAnalysis:
    edef:ElDef
    mps: ManParms
    el: Element
    fl: State
    tp: State
    ref_frame: g.Transformation
    results: Results | None = None

    def update(self, new_fl: State):
        new_el = self.el.match_intention(self.ref_frame, new_fl)
        new_tp = new_el.create_template(self.tp[0], new_fl.time)
        return ElementAnalysis(
            self.edef,
            self.mps,
            new_el,
            new_fl,
            new_tp,
            self.ref_frame
        )

    def plot_3d(self, **kwargs):
        from plotting import plotsec
        return plotsec(dict(fl=self.fl, tp=self.tp), **kwargs)

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.__dict__.items()}

    @staticmethod
    def from_dict(data) -> Self:
        mps = ManParms.from_dict(data['mps'])
        return ElementAnalysis(
            ElDef.from_dict(data['edef'], mps),
            mps,
            Element.from_dict(data['el']),
            State.from_dict(data['fl']),
            State.from_dict(data['tp']),
            g.Transformation.from_dict(data['ref_frame'])
        )
    
    def score_dg(self, dg: str):
        return self.edef.dgs[dg](self.el, self.fl, self.tp)

    def intra_score(self):
        return self.edef.dgs.apply(self.el, self.fl, self.tp) #[dg.apply(self.el.uid + (f'_{k}' if len(k) > 0 else ''), self.fl, self.tp) for k, dg in self.edef.dgs.items()]
    
    def info(self):
        return dict(
            element=self.el.uid,
            **(dict(angle=np.degrees(self.el.angle)) if "angle" in self.el.parameters else {}), 
            **(dict(radius=self.el.radius) if "radius" in self.el.parameters else {}),
            **(dict(rolls=np.degrees(self.el.rolls)) if "rolls" in self.el.parameters else {}),
            **(dict(roll=np.degrees(self.el.roll)) if "roll" in self.el.parameters else {}),
            freq=f"{1 / self.fl.dt.mean():.0f}",
            len=len(self.fl),
            **(dict(intra=f"{self.results.total:.4f}") if self.results is not None else {}),
        )  # fmt: skip
    


    def plot_results(self, name: str):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        result: Result = self.results[name]

        fig = make_subplots(
            1, 2,
            column_widths=[0.25, 0.75],
            specs=[[{"secondary_y": False,},{"secondary_y": True}]],
        )  # fmt: skip

        fig.add_trace(self.fl.pos.plotxz().data[0], row=1, col=1)

        
        fig.add_traces(
            [
                *result.measurement_trace(),
                *result.sample_trace(),
                result.downgrade_trace(),
            ],
            rows=1,
            cols=2,
        )
        fig.add_trace(
            result.visibility_trace(),
            row=1,
            col=2,
            secondary_y=True,
        )
        info = dict(
            **self.info(),
            **{"downgrade": result.total},
        )
        def format_float(v):
            return f"{v:.2f}" if isinstance(v, float) else v
        text = "<br>".join([f"{k}={format_float(v)}" for k, v in info.items()])

        fig.update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1),
            xaxis2=dict(range=[0, len(self.fl)]),
            height=300,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.0,
                xanchor="left",
                x=0.3,
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            #yaxis2=dict(range=[0, 2]),
            yaxis3=dict(range=[0, 1]),
            annotations=[
                go.layout.Annotation(
                    text=text,
                    align="left",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.2,
                    y=0.8,
                    bordercolor="black",
                    borderwidth=1,
                )
            ],
            scene=dict(
                aspectmode="data",
            ),
        )

        return fig
