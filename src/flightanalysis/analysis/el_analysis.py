from __future__ import annotations
from flightanalysis.definition.manparms import ManParms
import numpy as np

from flightanalysis.scoring.results import Results, Result
from flightdata import State
from typing import Self
from flightanalysis import ElDef, Element, Elements
from dataclasses import dataclass
import geometry as g


@dataclass
class ElementAnalysis:
    edef: ElDef
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
            self.edef, self.mps, new_el, new_fl, new_tp, self.ref_frame
        )

    def plot_3d(self, **kwargs):
        from plotting import plotsec

        return plotsec(dict(fl=self.fl, tp=self.tp), **kwargs)

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.__dict__.items()}

    @staticmethod
    def from_dict(data) -> Self:
        mps = ManParms.from_dict(data["mps"])
        return ElementAnalysis(
            ElDef.from_dict(data["edef"], mps),
            mps,
            Element.from_dict(data["el"]),
            State.from_dict(data["fl"]),
            State.from_dict(data["tp"]),
            g.Transformation.from_dict(data["ref_frame"]),
        )

    def info(self):
        return dict(
            element=self.el.uid,
            **(dict(angle=np.degrees(self.el.angle)) if "angle" in self.el.parameters else {}), 
            **(dict(radius=self.el.radius) if "radius" in self.el.parameters else {}),
            **(dict(rolls=np.degrees(self.el.rolls)) if "rolls" in self.el.parameters else {}),
            **(dict(roll=np.degrees(self.el.roll)) if "roll" in self.el.parameters else {}),
            freq=f"{1 / self.fl.dt.mean():.0f}",
            len=len(self.fl),
        )  # fmt: skip


    def axisplot(self, camera: dict = None, **kwargs):
        import plotly.graph_objects as go

        fig: go.Figure = self.plot_3d(**kwargs)
        fig.update_layout(
            scene=dict(
                camera=dict(
                    eye=dict(x=0, y=-1, z=0),
                    projection=dict(type="orthographic"),
                )
                | (camera if camera is not None else {}),
            )
        )
        return fig
