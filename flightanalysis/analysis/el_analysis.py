
from flightdata import State
from typing import Self
from flightanalysis.definition import ElDef
from flightanalysis.elements import Element
from dataclasses import dataclass
import geometry as g


@dataclass
class ElementAnalysis:
    edef:ElDef
    el: Element
    fl: State
    tp: State
    ref_frame: g.Transformation

    def plot_3d(self, origin=False, **kwargs):
        from flightplotting import plotsec
        return plotsec([self.fl, self.tp], 2, 5, origin=origin, **kwargs)

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.__dict__.items()}

    @staticmethod
    def from_dict(data) -> Self:
        return ElementAnalysis(
            ElDef.from_dict(data['edef']),
            Element.from_dict(data['el']),
            State.from_dict(data['fl']),
            State.from_dict(data['tp']),
            g.Transformation.from_dict(data['ref_frame'])
        )