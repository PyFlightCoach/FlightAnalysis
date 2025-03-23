from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from flightdata import Collection
from flightdata.base import to_list
from flightanalysis.scoring.measurement import Measurement
from flightanalysis.scoring.criteria import Criteria
from dataclasses import dataclass
import geometry as g
from itertools import chain
from .results import Results


class ElementsResults(Collection):
    """Intra Only
    Elements Results covers all the elements in a manoeuvre
    """

    VType = Results
    uid = "name"

    def __repr__(self):
        return f"ElementsResults, total = {self.total:.2f}, \n {super().__repr__()}"

    def score(self, difficulty=3, truncate=False):
        return sum([r.score(difficulty, truncate) for r in self])

    @property
    def total(self):
        return sum([r.total for r in self])

    @property
    def downgrade_list(self):
        return [r.total for r in self]

    def dg_dict(self):
        return {
            f"{k_el}_{k_crit}": result.total
            for k_el, results in self.data.items()
            for k_crit, result in results.data.items()
        }

    def downgrade_df(self):
        df = pd.concat([idg.downgrade_df().sum() for idg in self], axis=1).T
        df = pd.concat([df, pd.DataFrame(df.sum()).T])  # (np.floor(df.sum())).T])
        df.index = list(self.data.keys()) + ["Total"]

        return df

    def to_dict(self) -> dict[str, dict]:
        return dict(
            data={k: v.to_dict() for k, v in self.data.items()},
            summary=self.downgrade_list,
            total=float(self.total),
        )

    @staticmethod
    def from_dict(data) -> Results:
        return ElementsResults(
            {k: Results.from_dict(v) for k, v in data["data"].items()}
        )

    def intra_dg_list(self, cutoff=0.05):
        intra_dgs = self.downgrade_df().iloc[:-1].stack().sort_values(ascending=False)
        intra_dgs.columns = ["element", "name", "value"]
        return intra_dgs[intra_dgs > cutoff]
