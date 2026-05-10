from __future__ import annotations
from dataclasses import dataclass

from flightanalysis import Elements, measures as m, selectors as s, visors as v, Result
from flightdata import State
from .downgrade import DownGrade


@dataclass
class DGTest:
    dg: DownGrade
    els: Elements
    flown: State
    template: State

    def to_dict(self) -> dict:
        return dict(
            dg=self.dg.to_dict(),
            els=self.els.to_dict(),
            flown=self.flown.to_dict(),
            template=self.template.to_dict(),
        )
    
    @staticmethod
    def from_dict(d: dict) -> DGTest:
        return DGTest(
            dg=DownGrade.from_dict(d["dg"]),
            els=Elements.from_dict(d["els"]),
            flown=State.from_dict(d["flown"]),
            template=State.from_dict(d["template"]),
        )
    
    def run(self) -> Result:
        return self.dg(self.els, self.flown, self.template)