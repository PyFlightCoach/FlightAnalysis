from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy.typing as npt
from flightdata import State

from flightanalysis import Elements, Result
from flightanalysis.scoring.downgrade.applied_downgrade import AppliedDownGrade

from .manoeuvre_analysis import Analysis


@dataclass
class DynamicDownGrade:
    """Pre calculated optimisation space for a downgrade to facilitate faster segmentation optimisation."""
    adg: AppliedDownGrade
    side: Literal["left", "right"]
    boundary_id: int
    dgs: npt.NDArray

    @staticmethod
    def build(
        analysis: Analysis, dg_name: str, direction: Literal["left", "right"]
    ) -> None:

        adg = analysis.mdef.dgs[dg_name]

        if direction == "left" and adg.elements[0] == 0:
            raise ValueError(
                f"Cannot build left downgrade for {dg_name} as it starts at the first element."
            )
        if direction == "right" and adg.elements[-1] == len(analysis.manoeuvre.elements) - 1:
            raise ValueError(
                f"Cannot build right downgrade for {dg_name} as it ends at the last element."
            )

        els = Elements([analysis.manoeuvre.elements[el] for el in adg.elements])

        # extend the label to the limit (end of the adjacent element)
        full_flown = analysis.flown.step_label(
            "element",
            analysis.manoeuvre.elements[
                (adg.elements[0] - 1 if direction == "left" else adg.elements[-1])
            ].uid,
            f"{direction}_limit",
            analysis.flown.t,
            1,
        )


        flown = State.stack(
            {el.uid: full_flown.element[el.uid] for el in els}, "element"
        )

        template = State.stack(
            els.create_templates(analysis.templates[els[0].uid][0].transform, flown),
            "element",
        )

        res: Result = adg.dg(els, flown, template)

        incremental_error = res.criteria.local_error(res.sample, flown.dt, direction)
        incremental_dg = res.criteria.lookup(incremental_error)
        dgs = res.criteria.incremental_downgrade(incremental_dg, direction)

        return DynamicDownGrade(adg, direction, dgs), dgs



def build_bddgs(analysis: Analysis) -> list[list[DynamicDownGrade]]:
    """Builds a list of lists of DynamicDownGrade objects applicable to each element boundary in the manoeuvre."""
    bddgs = [[]] * (len(analysis.manoeuvre.elements)-1) 
    for adg in analysis.mdef.dgs.values():
        if adg.elements[0] > 0:
            bddgs[adg.elements[0] - 1].append(DynamicDownGrade.build(analysis, adg.name, "left"))
        if adg.elements[-1] < len(analysis.manoeuvre.elements) - 1:
            bddgs[adg.elements[-1]].append(DynamicDownGrade.build(analysis, adg.name, "right"))

    return bddgs