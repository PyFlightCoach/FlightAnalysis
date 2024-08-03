from __future__ import annotations
from flightdata import State
from dataclasses import dataclass
import numpy as np


@dataclass
class Subsetter:
    """A subset is a callable that takes a State and returns a list of indices
    It serialises and deserialises to a string, which references one of the predefined subsets
    in the Subsets class below along with some arguments relating to that subset.
    """

    name: str
    method: callable

    def __call__(self, fl: State, *args):
        return self.method(fl, *args)

    def __str__(self):
        return f'{self.name}({",".join([str(a) for a in self.args])})'


base_subsetters = [
    Subsetter("all", lambda fl: np.arange(len(fl))),
    Subsetter("last", lambda fl: np.array([-1])),
    Subsetter("first", lambda fl: np.array([0]))
]

@dataclass
class Subsetters:
    available: dict[str, Subsetter]

    def __getattr__(self, name):
        return lambda *args: lambda fl : self.available[name](fl, *args)

    def from_str(self, data: str):
        
        sargs = data.split("(")[1][:-1]
        args = [float(a) for a in sargs.split(",")] if len(sargs) > 0 else []
        return getattr(self, data.split("(")[0])(*args)

    @staticmethod
    def from_funcs(*funcs: list[callable]) -> Subsetters:
        subsetters = {s.name: s for s in base_subsetters}
        for func in funcs:
            subsetters[func.__name__] = Subsetter(func.__name__, func)
        return Subsetters(subsetters)



#this returns the slowing abs subset with the min_speed argument set to 5
#f3a_subsets.slowing_abs(5) 