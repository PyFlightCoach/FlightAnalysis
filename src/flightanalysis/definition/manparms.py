from __future__ import annotations
from itertools import product

from numbers import Number
from pathlib import Path
from typing import Callable, NamedTuple, Self

import numpy as np
import pandas as pd
from flightdata import Collection, State

from flightanalysis.base.utils import parse_csv
from flightanalysis.definition.operations import Opp
from flightanalysis.definition.manparm import ManParm
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.scoring import Combination, Comparison, Results
from flightanalysis.scoring import inter_visors as visors
from .combo_setting import ComboSetting
from .combo_settings import ComboSet, ComboSettings


class ManParms(Collection):
    VType = ManParm
    uid = "name"

    def collect(self, manoeuvre: Manoeuvre, state: State, box) -> Results:
        """Collect the comparison downgrades for each manparm for a given manoeuvre."""
        return Results(
            "Inter",
            [
                mp.get_downgrades(manoeuvre.all_elements(), state, box)
                for mp in self
                if isinstance(mp.criteria, Comparison) and len(mp.collectors)
            ],
        )

    def append_collectors(self, colls: dict[str, Callable]):
        """Append each of a dict of collector methods to the relevant ManParm"""
        for mp, col in colls.items():
            self.data[mp].append(col)

    def update_defaults(self, intended: Manoeuvre) -> Self:
        """Pull the parameters from a manoeuvre object and update the defaults of self based on the result of
        the collectors.

        Args:
            intended (Manoeuvre): Usually a Manoeuvre that has been resized based on an alinged state
        """
        mps = []
        for mp in self:
            flown_parm = list(mp.collect(intended.all_elements()).values())
            if len(flown_parm) > 0 and mp.defaul is not None:
                if isinstance(mp.criteria, Combination):
                    defaul = mp.criteria.check_option(
                        flown_parm, [col.index for col in mp.collectors]
                    )
                else:
                    defaul = np.mean(np.abs(flown_parm)) * np.sign(mp.defaul)
                mps.append(
                    ManParm(
                        mp.name,
                        mp.criteria,
                        defaul,
                        mp.unit,
                        mp.collectors,
                        mp.visibility,
                    )
                )
            else:
                mps.append(mp)
        return ManParms(mps)

    def set_values(self, **kwargs) -> Self:
        """Set the default values of the manparms to the kwargs provided"""
        mps = []
        for mp in self:
            if mp.name in kwargs:
                mps.append(
                    ManParm(
                        mp.name,
                        mp.criteria,
                        kwargs[mp.name],
                        mp.unit,
                        mp.collectors,
                        mp.visibility,
                    )
                )
            else:
                mps.append(mp)
        return ManParms(mps)

    def remove_unused(self):
        return ManParms([mp for mp in self if len(mp.collectors) > 0])

    def parse_rolls(
        self,
        rolls: Number | str | Opp | list[Number] | list[Opp],
        name: str,
        reversible: bool = True,
        turns: bool = False,
    ):
        if isinstance(rolls, Opp) or (
            isinstance(rolls, list) and all([isinstance(r, Opp) for r in rolls])
        ):
            return rolls
        elif isinstance(rolls, str) and not turns:
            return self.add(
                ManParm(
                    f"{name}_rolls", Combination.rollcombo(rolls, reversible), 0, "rad"
                )
            )
        elif isinstance(rolls, Number) or pd.api.types.is_list_like(rolls):
            return self.add(
                ManParm(
                    f"{name}_{'turns' if turns else 'rolls'}",
                    Combination.rolllist(
                        [rolls] if np.isscalar(rolls) else rolls, reversible
                    ),
                    0,
                    "rad",
                )
            )
        else:
            raise ValueError(
                f"Cannot parse {'turns' if turns else 'rolls'} from {rolls}"
            )

    def to_df(self):
        return pd.DataFrame(
            [
                [
                    mp.name,
                    mp.criteria.__class__.__name__,
                    mp.defaul,
                    mp.unit,
                    ",".join([str(v) for v in mp.collectors]),
                ]
                for mp in self
            ],
            columns=["name", "criteria", "default", "unit", "collectors"],
        )

    @staticmethod
    def parse_csv(file: str | Path, criteria: NamedTuple) -> ManParms:
        df = parse_csv(file, sep=";")
        mps = []
        for row in df.itertuples(index=False):
            mps.append(
                ManParm(
                    row.name,
                    getattr(criteria, row.criteria),
                    row.value,
                    row.unit,
                    visibility=visors.parse_csv_cell(row.visor)[0]
                    if row.visor and len(row.visor)
                    else None,
                )
            )
        return ManParms(mps)

    @property
    def combinations(self):
        return ManParms([mp for mp in self if isinstance(mp.criteria, Combination)])

    @property
    def comparisons(self):
        return ManParms([mp for mp in self if isinstance(mp.criteria, Comparison)])

    def permutations(self) -> list[ComboSettings]:
        """Get a list of all the possible combinations of the manparms with combination criteria."""
        all_settings = [
            [ComboSetting(mp.name, o) for o in range(len(mp.criteria))]
            for mp in self
            if isinstance(mp.criteria, Combination)
        ]
        if len(all_settings) == 0:
            return [None]
        else:
            return [ComboSettings(cs) for cs in list(product(*all_settings))]

    def clean_combosettings(self, cs_list: list[ComboSettings]):
        """Remove redundant entries from a list of combosettings.
        A combosettings is redundant if all other permutations of its mps are included in the list."""
        cleaned = []
        for i, cs in enumerate(cs_list):
            permutations = self.filter_keys(lambda k: k in cs.mp_names()).permutations()

            for j, checkcs in enumerate(cs_list):
                if checkcs.mp_names() == cs.mp_names():
                    for p in permutations:
                        if p == checkcs:
                            permutations.remove(p)
                            break
            if len(permutations) > 0:
                cleaned.append(cs)

        return cleaned

    def clean_comboset(self, cs: ComboSet):
        """Remove any combinations for which all possible values are included in the set."""
        cleaned = ComboSet()
        for mp in self.combinations.values():
            values = cs.collect_mp(mp.name)
            if len(values) == 0 or len(values) == len(mp.criteria):
                continue
            else:
                cleaned.add([ComboSetting(mp.name, v) for v in values], inplace=True)
        return cleaned
