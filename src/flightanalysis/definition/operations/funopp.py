from __future__ import annotations
from flightdata import Collection
from dataclasses import dataclass
from .operation import Opp, bracksplit
from numbers import Number
from typing import Callable, Literal


funs = ["abs", "sign", "max", "min"]

@dataclass
class FunOpp(Opp):
    """This class facilitates various functions that operate on Values and their serialisation"""
    opp: Literal["abs", "sign", "max", "min"]
    a: Opp | Number
    b: Opp | Number | None = None
    
    def __call__(self, *args, **kwargs):
        match self.opp:
            case 'abs':
                return abs(self.get_vf(self.a)(*args, **kwargs))
            case 'sign':
                return 1 if self.get_vf(self.a)(*args, **kwargs)>0 else -1
            case 'max':
                return max(self.get_vf(self.a)(*args, **kwargs), self.get_vf(self.b)(*args, **kwargs))
            case 'min':
                return min(self.get_vf(self.a)(*args, **kwargs), self.get_vf(self.b)(*args, **kwargs))
    
    def __str__(self):
        return f"{self.opp}({str(self.a)}{',' + str(self.b) if self.b else ''})"

    @staticmethod 
    def parse(inp: str, coll: Collection | Callable, name=None):
        for fun in funs:
            if inp.startswith(fun):
                args = bracksplit(inp[len(fun)+1:-1])
                return FunOpp(
                    name,
                    fun,
                    Opp.parse(args[0], coll, name),
                    Opp.parse(args[1], coll, name) if len(args)>1 else None,
                )
        raise ValueError(f"cannot read a FunOpp from the outside of {inp}")

    def list_parms(self):
        if isinstance(self.a, Opp):
            return self.a.list_parms()
        else:
            return []

def maxopp(name: str, a: Opp | Number, b: Opp | Number) -> FunOpp:
    return FunOpp(name, "max", a, b)

def minopp(name: str, a: Opp | Number, b: Opp | Number) -> FunOpp:
    return FunOpp(name, "min", a, b)