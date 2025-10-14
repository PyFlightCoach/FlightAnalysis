from flightanalysis.scoring.criteria.criteria_group import CriteriaGroup
from .base import DG
from .downgrade import DownGrade, dg
from .downgrade_pair import PairedDowngrade, pdg
from flightdata.base import Collection
from ..results import Results
from typing import Any
from pathlib import Path    
from ..reffuncs import measures as me, selectors as se, smoothers as sm
from flightanalysis.base.utils import parse_csv

def parse_downgrade_csv(file: Path | str, criteria: CriteriaGroup)  -> list[DG]:
    #TODO handle paired downgrades
    df = parse_csv(file)
    dgs: list[DownGrade | PairedDowngrade] = []
    for row in df.loc[df.kind=="dg"].itertuples(index=False):
        dgs.append(dg(
            row.display_name,
            me.parse_csv_cell(row.measure),
            sm.parse_csv_cell(row.smoother),
            se.parse_csv_cell(row.selector),
            criteria[row.criteria],
            row.tags
        ))

    return dgs

class DownGrades(Collection):
    VType = DG
    uid = "name"

    def apply(
        self,
        el: str | Any,
        fl,
        tp,
        limits=True,
        mkwargs: dict = None,
        smkwargs: dict = None,
        sekwargs: dict = None,
    ) -> Results:        
        res = Results(el if isinstance(el, str) else el.uid, [])
        for downgrade in self:
            res.add(downgrade(el, fl, tp, limits, mkwargs, smkwargs, sekwargs))
        return res

    def to_list(self):
        return [downgrade.name for downgrade in self]


