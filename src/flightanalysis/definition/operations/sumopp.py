from __future__ import annotations
from flightdata import Collection
from dataclasses import dataclass
from .operation import Opp
from numbers import Number
from itertools import chain
from typing import Callable


@dataclass
class SumOpp(Opp):
    """This class sums a list of values"""
    vals: list[Opp | Number]

    def __call__(self, mps, **kwargs):
        return sum([self.get_vf(v)(mps, **kwargs) for v in self.vals])

    def __str__(self):
        return f"sum([{','.join([str(v) for v in self.vals])}])"
    
    @staticmethod
    def parse(inp: str, coll: Collection | Callable, name=None):
        if inp.startswith("sum"):
            return SumOpp(
                name,
                [Opp.parse(val, coll, name) for val in inp[5:-2].split(',')]
            )
        raise ValueError(f"cannot read a SumOpp from the outside of {inp}")
    
    def list_parms(self):
        return list(chain(*[v.list_parms() for v in self.vals if isinstance(v, Opp)]))