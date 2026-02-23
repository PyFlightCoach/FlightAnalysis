from __future__ import annotations
from dataclasses import dataclass, field
from numbers import Number
from typing import Tuple

import numpy as np
from flightdata import Collection, State
from geometry import Point
from flightanalysis.base.ref_funcs import RefFunc
from flightanalysis.elements import Elements
from flightanalysis.scoring import (
    Combination,
    Comparison,
    Criteria,
    Measurement,
    Result,
    Single,
    inter_visors as visors,
)
from .collectors import Collector, Collectors
from .operations import Opp


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

    criteria: Comparison | Combination
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

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            name=self.name,
            criteria=self.criteria.to_dict(criteria_names),
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
            visibility=visors.parse(data["visibility"])
            if "visibility" in data
            else None,
        )

    def append(self, collector: Opp | Collector | Collectors):
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
    def s_parse(opp: str | Opp | list[str], mps: Collection):
        """Serialise and parse a manparm in order to link it to the new collection"""
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

    def get_downgrades(self, els: Elements, state: State, box) -> Result:
        direction, visor = self.collect_vis(els, state, box)
        
        measurement = Measurement(
            np.array([c(els) for c in self.collectors]),
            direction,
            self.unit,
            [str(c) for c in self.collectors],
        )

        visibility = np.array(
            [visor[0]] + [max(va, vb) for va, vb in zip(visor[:-1], visor[1:])]
        )


        mistakes, dgs, ids = self.criteria(measurement.value)

        return Result(
            self.name,
            measurement,
            visibility,
            measurement.value,
            np.arange(len(measurement)),
            mistakes,
            dgs * visibility,
            ids,
            self.criteria,
        )

    @property
    def value(self):
        if isinstance(self.criteria, Combination):
            return self.criteria[self.defaul]
        else:
            return self.defaul

    def __call__(self, *args, **kwargs):
        return self.value

    @property
    def kind(self):
        return self.criteria.__class__.__name__

    def copy(self, **kwargs) -> ManParm:
        return ManParm(
            name=kwargs.get("name", self.name),
            criteria=kwargs.get("criteria", self.criteria),
            defaul=kwargs.get("defaul", self.defaul),
            unit=kwargs.get("unit", self.unit),
            collectors=kwargs.get("collectors", self.collectors.copy()),
            visibility=kwargs.get("visibility", self.visibility),
        )

    def list_parms(self):
        return [self]

    def __repr__(self):
        return f"ManParm({self.name}, {self.criteria.__class__.__name__}, {self.defaul}, {self.unit}, {str(self.visibility) if self.visibility else 'None'})"



