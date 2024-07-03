from __future__ import annotations
from flightdata import Collection
from dataclasses import dataclass
from .operation import Opp
from numbers import Number


@dataclass
class FunOpp(Opp):
    """This class facilitates various functions that operate on Values and their serialisation"""
    funs = ["abs"]
    a: Opp | Number
    opp: str

    def __call__(self, mps, **kwargs):
        return {
            'abs': abs(self.get_vf(self.a)(mps, **kwargs))
        }[self.opp]
    
    def __str__(self):
        return f"{self.opp}({str(self.a)})"

    @staticmethod 
    def parse_f(inp: str, parser, name=None):
        for fun in FunOpp.funs:
            if inp.startswith(fun):
                return FunOpp(
                    name,
                    Opp.parse_f(inp[len(fun)+1:-1], parser, name), 
                    fun
                )
        raise ValueError(f"cannot read a FunOpp from the outside of {inp}")

    @staticmethod 
    def parse(inp: str, coll: Collection, name=None):
        for fun in FunOpp.funs:
            if inp.startswith(fun):
                return FunOpp(
                    name,
                    coll.VType.parse(inp[len(fun)+1:-1], coll), 
                    fun
                )
        raise ValueError(f"cannot read a FunOpp from the outside of {inp}")

    def list_parms(self):
        if isinstance(self.a, Opp):
            return self.a.list_parms()
        else:
            return []