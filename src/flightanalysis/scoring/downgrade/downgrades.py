from collections import namedtuple
from .base import DG
from .downgrade import DownGrade, dg
from .downgrade_pair import PairedDowngrade, pdg
from flightdata.base import Collection
from ..results import Results
from typing import Any, NamedTuple
from pathlib import Path
from flightanalysis.scoring.reffuncs import measures as me, selectors as se, visors as vi
from flightanalysis.base.utils import parse_csv
from flightanalysis.elements.tags import DGTags


def parse_downgrade_csv(file: Path | str, intra_criteria: NamedTuple) -> list[DG]:
    df = parse_csv(file, sep=";")
    downgrades: dict[str : DownGrade | PairedDowngrade] = {}
    for name, dgs in df.groupby("unique_name"):
        new_dgs = [
            dg(
                row.display_name,
                me.parse_csv_cell(row.measure)[0],
                se.parse_csv_cell(row.selector),
                getattr(intra_criteria, row.criteria),
                DGTags.parse(row.last, row.this, row.next),
            )
            for row in dgs.itertuples(index=False)
        ]
        if len(new_dgs) == 1:
            downgrades[name] = new_dgs[0]
        elif len(new_dgs) == 2:
            assert new_dgs[0].tags == new_dgs[1].tags, "downgrades with same name must have same tags"
            downgrades[name] = pdg(name, *new_dgs, new_dgs[0].tags)
        else:
            raise ValueError(f"Expected 1 or 2 downgrades with unique name {name}, got {len(new_dgs)}")

    return namedtuple("Downgrades", downgrades.keys())(*downgrades.values())


class DownGrades(Collection):
    VType = DG
    uid = "name"

    def apply(
        self,
        el: str | Any,
        fl,
        tp,
        limits=True,
    ) -> Results:
        res = Results(el if isinstance(el, str) else el.uid, [])
        for downgrade in self:
            res.add(downgrade(el, fl, tp))
        return res

    def to_list(self):
        return [downgrade.name for downgrade in self]
