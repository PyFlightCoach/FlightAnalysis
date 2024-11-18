from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Number
from typing import Any, Callable, Dict, Self, Tuple, Union

import geometry as g
import numpy as np
import pandas as pd
from flightdata import Collection, State
from geometry import Point

from flightanalysis.base.ref_funcs import RefFunc
from flightanalysis.elements import Elements
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.scoring import (
    Combination,
    Comparison,
    Criteria,
    Measurement,
    Result,
    Results,
    Single,
    visor,
)

from . import Collector, Collectors, Opp


@dataclass
class ManParm(Opp):
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction.
        name (str): a short name, must work as an attribute so no spaces or funny characters
        criteria (Comparison): The comparison criteria function to be used when judging this parameter
        defaul (float): A default value (or default option if specified in criteria)
        collectors (Collectors): a list of functions that will pull values for this parameter from an Elements
            collection. If the manoeuvre was flown correctly these should all be the same. The resulting list
            can be passed through the criteria (Comparison callable) to calculate a downgrade.

    """

    criteria: Criteria
    defaul: Number = None
    unit: str = "m"
    collectors: Collectors = field(default_factory=Collectors)
    visibility: RefFunc = None

    @property
    def n(self):
        return (
            len(self.criteria.desired[0])
            if isinstance(self.criteria, Combination)
            else None
        )

    def to_dict(self):
        return dict(
            name=self.name,
            criteria=self.criteria.to_dict(),
            defaul=self.defaul,  # because default is reserverd in javascript
            unit=self.unit,
            collectors=self.collectors.to_dict(),
            visibility=str(self.visibility),
        )

    @staticmethod
    def from_dict(data: dict):
        return ManParm(
            name=data["name"],
            criteria=Criteria.from_dict(data["criteria"]),
            defaul=data["defaul"],
            unit=data["unit"],
            collectors=Collectors.from_dict(data["collectors"]),
            visibility=visor.parse(data["visibility"]) if "visibility" in data else None,
        )

    def append(self, collector: Union[Opp, Collector, Collectors]):
        if isinstance(collector, Opp) or isinstance(collector, Collector):
            self.collectors.add(collector)
        elif isinstance(collector, Collectors):
            for coll in collector:
                self.append(coll)
        else:
            raise ValueError(
                f"expected a Collector or Collectors not {collector.__class__.__name__}"
            )

    @staticmethod
    def s_parse(opp: str | Opp | list[str] | Any, mps: Collection):
        try:
            if isinstance(opp, Opp) or isinstance(opp, str):
                opp = ManParm.parse(str(opp), mps)
            elif isinstance(opp, list) and all([isinstance(o, str) for o in opp]):
                opp = [ManParm.parse(str(op), mps) for op in opp]
        except Exception:
            pass
        return opp

    def assign(self, id, collector):
        self.collectors.data[id] = collector

    def collect(self, els: Elements):
        return {str(collector): collector(els) for collector in self.collectors}

    def collect_vis(
        self, els: Elements, state: State, box
    ) -> Tuple[Point, list[float]]:
        if self.visibility:
            _vis = np.array(
                [
                    self.visibility(c.extract_state(els, state), box)
                    for c in self.collectors
                ]
            )
        else:
            _vis = np.ones(len(self.collectors))
        return (
            Point.concatenate(
                [c.extract_state(els, state).pos.mean().unit() for c in self.collectors]
            ),
            _vis,
        )

    def get_downgrades(self, els: Elements, state: State, box):
        direction, visor = self.collect_vis(els, state, box)

        meas = Measurement(
            [c(els) for c in self.collectors],
            self.unit,
            direction,
            np.array(
                [visor[0]] + [max(va, vb) for va, vb in zip(visor[:-1], visor[1:])]
            ),
            [str(c) for c in self.collectors],
        )
        mistakes, dgs, ids = self.criteria(meas.value)
        return Result(
            self.name,
            meas,
            None,
            meas.value,
            np.arange(len(meas.value)),
            mistakes,
            dgs * meas.visibility,
            ids,
            self.criteria,
        )

    @property
    def value(self):
        if isinstance(self.criteria, Comparison):
            return self.defaul
        elif isinstance(self.criteria, Combination):
            return self.criteria[self.defaul]
        else:
            raise AttributeError("This type of ManParm has no value")

    @property
    def kind(self):
        return self.criteria.__class__.__name__

    def copy(self):
        return ManParm(
            name=self.name,
            criteria=self.criteria,
            defaul=self.defaul,
            unit=self.unit,
            collectors=self.collectors.copy(),
            visibility=self.visibility,
        )

    def list_parms(self):
        return [self]

    def __repr__(self):
        return f"ManParm({self.name}, {self.criteria.__class__.__name__}, {self.defaul}, {self.unit}, {str(self.visibility) if self.visibility else 'None'})"


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
                if not isinstance(mp.criteria, Combination)
            ],
        )

    def append_collectors(self, colls: Dict[str, Callable]):
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
                    defaul = mp.criteria.check_option(flown_parm)
                else:
                    defaul = np.mean(np.abs(flown_parm)) * np.sign(mp.defaul)
                mps.append(
                    ManParm(mp.name, mp.criteria, defaul, mp.unit, mp.collectors, mp.visibility)
                )
            else:
                mps.append(mp)
        return ManParms(mps)

    def remove_unused(self):
        return ManParms([mp for mp in self if len(mp.collectors) > 0])

    def parse_rolls(
        self, rolls: Union[Number, str, Opp, list], name: str, reversible: bool = True
    ):
        if isinstance(rolls, Opp) or (
            isinstance(rolls, list) and all([isinstance(r, Opp) for r in rolls])
        ):
            return rolls
        elif isinstance(rolls, str):
            return self.add(
                ManParm(
                    f"{name}_rolls", Combination.rollcombo(rolls, reversible), 0, "rad"
                )
            )
        elif isinstance(rolls, Number) or pd.api.types.is_list_like(rolls):
            return self.add(
                ManParm(
                    f"{name}_rolls",
                    Combination.rolllist(
                        [rolls] if np.isscalar(rolls) else rolls, reversible
                    ),
                    0,
                    "rad",
                )
            )
        else:
            raise ValueError(f"Cannot parse rolls from {rolls}")

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


class DummyMPs:
    def __getattr__(self, name):
        return ManParm(name, Single(), 0)


def scale_vis(fl: State, box):
    # factor of 1 when it takes up 1/2 of the box height.
    # reduces to zero for zero length el
    depth = fl.pos.y.mean()

    h = box.top_pos(g.PY(depth)) - box.bottom_pos(g.PY(depth))

    _range = fl.pos.max() - fl.pos.min()
    length = abs(_range)[0]
    return min(1, 4 * length / h.z[0])  # np.tan(np.radians(60)) / 2
