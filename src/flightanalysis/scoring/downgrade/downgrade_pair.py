from typing import Tuple
import numpy as np
from dataclasses import dataclass, replace
from .base import DG
from .downgrade import DownGrade
from ..results import Result
from flightanalysis.elements import Elements

from flightanalysis.elements.tags import DGTags

@dataclass
class PairedDowngrade(DG):
    """A pair of downgrades, the result transitions from first to second at the point that
    gives the smallest downgrade

    Paired downgrades don't support selectors or smoothing, and only instantanious
    measurements (those that depend only on the current datapoint) can be used.
    """
    first: DownGrade
    second: DownGrade

    def rename(self, name: str):
        return replace(self, name=name)

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            name=self.name,
            tags=self.tags.to_dict() if self.tags else None,
            first=self.first.to_dict(criteria_names),
            second=self.second.to_dict(criteria_names),
        )



    def __call__(
        self,
        el,
        fl,
        tp,
        limits=True,
        mkwargs: dict = None,
        smkwargs: dict = None,
        sekwargs: dict = None,
    ) -> Tuple[Result]:

        m1 = self.first.measure(Elements([el]), fl, tp, **(mkwargs or {}))
        m2 = self.second.measure(Elements([el]), fl, tp, **(mkwargs or {}))

        rs1 = self.first.create_sample(m1)
        rs2 = self.second.create_sample(m2)

        idg1 = self.first.criteria.calculate_increments(rs1, "forward")
        idg2 = self.second.criteria.calculate_increments(rs2, "backward")

        splitindex = (idg1 + idg2).argmin()

        return (
            Result(
                f"{self.name}_{self.first.name}",
                m1[: splitindex + 1],
                rs1[: splitindex + 1],
                rs1[: splitindex + 1],
                np.arange(splitindex+1),
                *self.first.criteria(rs1[: splitindex + 1], limits),
                self.first.criteria,
            ),
            Result(
                f"{self.name}_{self.second.name}",
                m2[splitindex:],
                rs2[splitindex:],
                rs2[splitindex:],
                np.arange(splitindex, len(fl)),
                *self.second.criteria(rs2[splitindex:], limits),
                self.second.criteria,
            ),
        )


def pdg(
    name: str,
    first: DownGrade,
    second: DownGrade,
    tags: DGTags
) -> PairedDowngrade:
    """Create a paired downgrade from two downgrades"""
    return PairedDowngrade(name, tags, first, second)
