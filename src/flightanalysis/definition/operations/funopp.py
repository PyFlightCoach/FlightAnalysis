from __future__ import annotations
from flightdata import Collection
from dataclasses import dataclass
from .operation import Opp
from numbers import Number
from typing import Callable


@dataclass
class FunOpp(Opp):
    """This class facilitates various functions that operate on Values and their serialisation"""
    funs = ["abs", "sign"]
    a: Opp | Number
    opp: str

    def __call__(self, mps, **kwargs):
        return {
            'abs': abs(self.get_vf(self.a)(mps, **kwargs)),
            'sign': 1 if self.get_vf(self.a)(mps, **kwargs)>0 else -1
        }[self.opp]
    
    def __str__(self):
        return f"{self.opp}({str(self.a)})"

    @staticmethod 
    def parse(inp: str, coll: Collection | Callable, name=None):
        for fun in FunOpp.funs:
            if inp.startswith(fun):
                return FunOpp(
                    name,
                    Opp.parse(inp[len(fun)+1:-1], coll, name), 
                    fun
                )
        raise ValueError(f"cannot read a FunOpp from the outside of {inp}")

    def list_parms(self):
        if isinstance(self.a, Opp):
            return self.a.list_parms()
        else:
            return []