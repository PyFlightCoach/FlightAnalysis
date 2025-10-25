from __future__ import annotations
import pandas as pd
from flightdata import Collection
from .results import Results
from flightanalysis.scoring.criteria import Criteria
from more_itertools import flatten
from flightanalysis.base.utils import df_insert

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
    
    def _criteria_filter(self, key: str, key_by_criteria: bool=False):
        odata = [v.criteria_filter(key, key_by_criteria) for v in self.values()]
        return list(flatten(odata))

    def criteria_filter(self, key: str | list[str], key_by_criteria: bool=False):
        if isinstance(key, str):
            self._criteria_filter(key, key_by_criteria)
        else:
            return list(flatten([self._criteria_filter(k, key_by_criteria) for k in key]))
        
    def criteria_sum(self, key_by_criteria: bool=False) -> dict[str, float]:
        sums = {}
        for results in self:
            for k, v in results.criteria_sum(key_by_criteria).items():
                sums[k] = sums[k] + v if k in sums else v                    
        return sums
        
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

    def replace_criteria(self, *args: list[Criteria], limits: bool=True, **kwargs: dict[str, Criteria]):
        """recalculate the results by replacing selected criteria
            *args will replace all criteria with matching names
            **kwargs will replace criteria in downgrades with matching keys
            If there is a conflict, kwargs will take precedence
        """
        return ElementsResults({k: v.replace_criteria(*args, limits=limits, **kwargs) for k, v in self.items()})

    def tuning_data(self):
        return pd.concat(
            [df_insert(r.tuning_data(), type="intra", element=k) for k, r in self.items()], ignore_index=True
        )