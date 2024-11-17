from __future__ import annotations
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
    
    def intra_score(self):
        return self.edef.dgs.apply(self.el, self.fl, self.tp) #[dg.apply(self.el.uid + (f'_{k}' if len(k) > 0 else ''), self.fl, self.tp) for k, dg in self.edef.dgs.items()]
    
