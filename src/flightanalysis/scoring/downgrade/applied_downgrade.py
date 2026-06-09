"""
Links a downgrade to consecutive elements
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from flightdata import State
from flightdata.base import Collection

from flightanalysis.elements import Elements
from flightanalysis.scoring.results import Result, Results

from .downgrade import DownGrade, SquashError
from .downgrade_pair import PairedDownGrade
from .linkers import Linker, Linkers


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

    @property
    def dg(self):
        return self.dgs[0]

    def score(
        self, elements: Elements, templates: dict[str, State], flown: State
    ) -> Result:
        return self.dg(
            elements.filter_indices(self.elements.__contains__),
            State.stack([flown.element[elements[el].uid] for el in self.elements]),
            State.stack([templates[elements[el].uid] for el in self.elements]),
        )

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            name=self.name,
            dgs=[dg.to_dict(criteria_names) for dg in self.dgs],
            elements=self.elements,
        )

    @staticmethod
    def from_dict(data: dict) -> AppliedDownGrade:
        return AppliedDownGrade(
            name=data["name"],
            dgs=[DownGrade.from_dict(dg) for dg in data["dgs"]],
            elements=data["elements"],
        )

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

    def score(
        self, elements: Elements, templates: dict[str, State], flown: State
    ) -> Results:
        res = []
        for adg in self.values():
            res.append(adg.score(elements, templates, flown))
        return Results("inta", res)

    def boundary_filter(self, index: int) -> AppliedDownGrades:
        return self.filter_values(lambda adg: index in [adg.elements[0]-1, adg.elements[-1]])
