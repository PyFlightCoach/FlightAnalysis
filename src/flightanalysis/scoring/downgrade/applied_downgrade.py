"""
Links a downgrade to consecutive elements
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from flightdata.base import Collection
from flightdata import State

from .downgrade import DownGrade
from .downgrade_pair import PairedDownGrade
from .linkers import Linkers, Linker
from flightanalysis.elements import Elements


@dataclass
class AppliedDownGrade:
    name: str
    dgs: list[DownGrade | PairedDownGrade]
    elements: list[int]

    def __repr__(self):
        return f"{self.dgs[0].display_name} applied to {', '.join([str(e) for e in self.elements])}"

    @property
    def dg_names(self) -> list[str]:
        return [dg.name for dg in self.dgs]


class AppliedDownGrades(Collection[AppliedDownGrade]):
    uid = "name"

    def add_or_update(
        self,
        elements: Elements,
        templates: dict[str, State],
        index: int,
        dg: DownGrade,
        linkers: Linkers,
        inplace: bool = False,
    ) -> AppliedDownGrades:
        el1 = elements[index]
        for adg in self.values():
            if index != adg.elements[-1] + 1:
                continue
            linker = linkers.find_linker(adg.dg_names[-1], dg.name)
            if linker is None:
                continue
            el0 = elements[adg.elements[-1]]
            if not linker.check(
                el0,
                templates[el0.uid],
                el1,
                templates[el1.uid],
            ):
                continue
            new_adg = replace(
                adg,
                elements=adg.elements + [index],
                dgs=adg.dgs + [dg],
            )
            return self.add(new_adg, inplace)
        else:
            return self.add(
                AppliedDownGrade(
                    name=f"{dg.name}_{index}",
                    dgs=[dg],
                    elements=[index],
                ),
                inplace,
            )
