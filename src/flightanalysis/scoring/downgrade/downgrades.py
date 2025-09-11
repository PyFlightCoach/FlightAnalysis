from .dg import DG
from flightdata.base import Collection
from ..results import Results
from typing import Any
from itertools import chain

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
        for dg in self:
            res.add(dg(el, fl, tp, limits, mkwargs, smkwargs, sekwargs))
        return res

    def to_list(self):
        return [dg.name for dg in self]

