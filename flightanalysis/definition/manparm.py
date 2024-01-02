from typing import Dict, Callable, Union, Tuple
import numpy as np
from flightdata import Collection
from flightanalysis.manoeuvre import Manoeuvre
from flightdata import State
from flightanalysis.scoring import *
from . import Collector, Collectors, Opp
from dataclasses import dataclass, field
from typing import Any, Self
import numpy as np
import pandas as pd
from geometry import Point
from numbers import Number
from copy import deepcopy

@dataclass
class ManParm(Opp):
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction. 
        name (str): a short name, must work as an attribute so no spaces or funny characters
        criteria (Comparison): The comparison criteria function to be used when judging this parameter
        default (float): A default value (or default option if specified in criteria)
        collectors (Collectors): a list of functions that will pull values for this parameter from an Elements 
            collection. If the manoeuvre was flown correctly these should all be the same. The resulting list 
            can be passed through the criteria (Comparison callable) to calculate a downgrade.

    """
    criteria: Criteria
    default:Any=None
    collectors:Collectors=field(default_factory=lambda : Collectors())


    @property
    def n(self):
        return len(self.criteria.desired[0]) if isinstance(self.criteria, Combination) else None
        
    def to_dict(self):
        return dict(
            name = self.name,
            criteria = self.criteria.to_dict(),
            default = self.default,
            collectors = self.collectors.to_dict()
        )
    
    @staticmethod
    def from_dict(data: dict):
        return ManParm(
            name = data["name"],
            criteria = Criteria.from_dict(data["criteria"]),
            default = data["default"] if 'default' in data else data['defaul'], # because default is reserverd in javascript
            collectors = Collectors.from_dict(data["collectors"])
        )

    def append(self, collector: Union[Opp, Collector, Collectors]):
        if isinstance(collector, Opp) or isinstance(collector, Collector):
            self.collectors.add(collector)    
        elif isinstance(collector, Collectors):
            for coll in collector:
                self.append(coll)
        else:
            raise ValueError(f"expected a Collector or Collectors not {collector.__class__.__name__}")

    def assign(self, id, collector):
        self.collectors.data[id] = collector

    def collect(self, els):
        return {str(collector): collector(els) for collector in self.collectors}

    def collect_vis(self, els, state: State) -> Tuple[Point, list[float]]:
        vis = [[c.visibility(els, state) for c in collector.list_parms()] for collector in self.collectors]

        return Point.concatenate([Point.concatenate([v[0] for v in vi]).mean() for vi in vis ]), [np.mean([v[1]for v in vi]) for vi in vis]


    def get_downgrades(self, els, state: State):
        coll = self.collect(els)
        values = list(coll.values())
        direction, vis = self.collect_vis(els, state)

        meas = Measurement(
            values,
            self.default,
            direction,
            vis
        )

        keys, errors, dgs = self.criteria(list(coll.keys()), list(coll.values())) 
        return Result(self.name, meas, values, errors, dgs * meas.visibility, keys)

    @property
    def value(self):
        if isinstance(self.criteria, Comparison):
            return self.default
        elif isinstance(self.criteria, Combination):
            return self.criteria[self.default]
        else:
            raise AttributeError("This type of ManParm has no value")


    @property
    def kind(self):
        return self.criteria.__class__.__name__    

    def copy(self):
        return ManParm(name=self.name, criteria=self.criteria, default=self.default, collectors=self.collectors.copy())

    def list_parms(self):
        return [self]

    def __repr__(self):
        return f'ManParm({self.name}, {self.criteria.__class__.__name__}, {self.default})'



class ManParms(Collection):
    VType=ManParm
    uid="name"

    def collect(self, manoeuvre: Manoeuvre, state: State=None) -> Results:
        """Collect the comparison downgrades for each manparm for a given manoeuvre."""
        return Results(
            "Inter",
            [mp.get_downgrades(manoeuvre.all_elements(), state) for mp in self if not isinstance(mp.criteria, Combination)]
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
            if len(flown_parm) > 0 and mp.default is not None:
                if isinstance(mp.criteria, Combination):
                    default = mp.criteria.check_option(flown_parm)
                else:
                    default = np.mean(np.abs(flown_parm)) * np.sign(mp.default)
                mps.append(ManParm(mp.name, mp.criteria, default, mp.collectors))
            else: 
                mps.append(mp)
        return ManParms(mps)
    
    def remove_unused(self):
        return ManParms([mp for mp in self if len(mp.collectors) > 0])


    def parse_rolls(self, rolls: Union[Number, str, Opp], name: str, reversible: bool=True):
        if isinstance(rolls, Opp):
            return rolls
        elif isinstance(rolls, str):
            return self.add(ManParm(f"{name}_rolls", Combination.rollcombo(rolls, reversible), 0))
        elif isinstance(rolls, Number) or pd.api.types.is_list_like(rolls):
            return self.add(ManParm(f"{name}_rolls", 
                Combination.rolllist(
                    [rolls] if np.isscalar(rolls) else rolls, 
                    reversible
            ), 0) )
        else:
            raise ValueError(f"Cannot parse rolls from {rolls}")




class DummyMPs:
    def __getattr__(self, name):
        return ManParm(name, Single(), 0)
    