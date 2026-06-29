from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

import numpy.typing as npt
from flightdata import State

from flightanalysis import Elements, Result
from flightanalysis.scoring.downgrade.applied_downgrade import AppliedDownGrade

from .manoeuvre_analysis import Analysis
from loguru import logger


@dataclass
class DynamicDownGrade:
    """Pre calculated optimisation space for a downgrade to facilitate faster segmentation optimisation."""

    adg: AppliedDownGrade
    side: Literal["left", "right"]
    boundary_id: int
    dgs: npt.NDArray

    @staticmethod
    def can_build(
        adg: AppliedDownGrade, direction: Literal["left", "right"], analysis: Analysis, sink: Callable[[str], None] = logger.debug
    ) -> bool:
        """Check if the downgrade can be built for the given side and element boundary."""
        if direction == "left" and adg.elements[0] == 0:
            sink(
                f"Cannot build left for {adg.name} as it starts at the first element."
            )
            return False
        if (
            direction == "right"
            and adg.elements[-1] == len(analysis.manoeuvre.elements) - 1
        ):
            sink(
                f"Cannot build right for {adg.name} as it ends at the last element."
            )
            return False

        for selector in adg.dgs[0 if direction == "left" else -1].selectors:
            if not getattr(selector, direction):
                sink(
                    f"Cannot build {direction} for {adg.name} as selector {selector.name} chops off the {direction} of the {'first' if direction == 'left' else 'last'} element"
                )
                return False

        # check the selectors
        return True

    @staticmethod
    def build(
        analysis: Analysis, dg_name: str, direction: Literal["left", "right"]
    ) -> "DynamicDownGrade":

        adg = analysis.mdef.dgs[dg_name]
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

        return DynamicDownGrade(
            adg,
            direction,
            adg.elements[0] if direction == "left" else adg.elements[-1],
            dgs,
        )


def build_bddgs(analysis: Analysis) -> list[list[DynamicDownGrade]]:
    """Builds a list of lists of DynamicDownGrade objects applicable to each element boundary in the manoeuvre."""
    bddgs = [[]] * (len(analysis.manoeuvre.elements) - 1)
    for adg in analysis.mdef.dgs.values():
        for side in ["left", "right"]:
            if DynamicDownGrade.can_build(adg, side, analysis, logger.debug):
                ddg = DynamicDownGrade.build(analysis, adg.name, side)
                elindex = (
                    ddg.adg.elements[0] - 1 if side == "left" else ddg.adg.elements[-1]
                )
                bddgs[elindex].append(ddg)

    return bddgs
