from __future__ import annotations
import pandas as pd
from dataclasses import dataclass
from .results import Results
from .elements_results import ElementsResults
from .dgplot import DGPlot


@dataclass
class ManoeuvreResults:
    inter: Results
    intra: ElementsResults
    positioning: Results

    def dg_dict(self):
        return dict(
            **self.intra.dg_dict(),
            **self.inter.dg_dict(),
            **self.positioning.dg_dict(),
        )

    def summary(self):
        return {k: v.total for k, v in self.__dict__.items() if v is not None}

    def score_summary(self, difficulty=3, truncate=False):
        intra = self.intra.score(difficulty, "results" if truncate else None)
        inter = self.inter.score(difficulty, "result" if truncate else None)
        positioning = self.positioning.score(difficulty, "result" if truncate else None)
        return dict(
            intra=float(intra),
            inter=float(float(inter)),
            positioning=float(float(positioning)),
            total=float(max(10 - intra - inter - positioning, 0)),
        )

    def score(self, difficulty=3, truncate: bool = False):
        return self.score_summary(difficulty, truncate)["total"]

    def to_dict(self):
        return dict(
            inter=self.inter.to_dict(),
            intra=self.intra.to_dict(),
            positioning=self.positioning.to_dict(),
            summary=self.summary(),
            score=self.score(),
        )

    @staticmethod
    def from_dict(data):
        return ManoeuvreResults(
            Results.from_dict(data["inter"]),
            ElementsResults.from_dict(data["intra"]),
            Results.from_dict(data["positioning"]),
        )

    def fcj_results(self):
        res = []
        for diff in [1, 2, 3]:
            for trunc in [False, True]:
                res.append(
                    dict(
                        score=self.score_summary(diff, trunc),
                        properties=dict(difficulty=diff, truncate=trunc),
                    )
                )
        return res

    def el_dg_list(self, man, cutoff=0.05):
        intra_dgs = self.intra.intra_dg_list(cutoff)
        inter_dgs = self.inter.inter_dg_list(cutoff)

        dgs = pd.concat([inter_dgs, intra_dgs])  # , keys=['inter', 'intra'])

        grps = []
        for grp in dgs.groupby(level=0).groups.items():
            grps.append(
                DGPlot(
                    grp[0],
                    {g[1]: float(dgs.loc[grp[0], g[1]]) for g in grp[1]},
                    getattr(man, grp[0]).fl.pos.mean(),
                )
            )
        return grps

