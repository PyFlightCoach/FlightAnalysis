from __future__ import annotations
from flightdata import Collection
from dataclasses import dataclass
from numbers import Number
from .operation import Opp
from typing import Callable

oplu = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b
}

@dataclass
class MathOpp(Opp):
    """This class facilitates various ManParm opperations and their serialisation"""
    a: Opp | Number
    b: Opp | Number
    opp: str

    def __call__(self, mps, **kwargs):
        return oplu[self.opp](
            self.get_vf(self.a)(mps, **kwargs), 
            self.get_vf(self.b)(mps, **kwargs)
        )

    def __str__(self):
        return f"({str(self.a)}{self.opp}{str(self.b)})"

    @staticmethod
    def parse(inp:str, coll: Collection | Callable, name:str=None):
        if inp.startswith("(") and inp.endswith(")"):
            bcount = 0
            for i, l in enumerate(inp):
                bcount += 1 if l=="(" else 0
                bcount -=1 if l==")" else 0
            
                if bcount == 1 and l in oplu.keys() and i>1:
                    return MathOpp(
                        name,
                        Opp.parse(inp[1:i], coll, name),
                        Opp.parse(inp[i+1:-1], coll, name),
                        l
                    )
                    
        raise ValueError(f"cannot read an MathOpp from the outside of {inp}")

    def list_parms(self) -> list[str]:
        parms = []
        if isinstance(self.a, Opp):
            parms = parms + self.a.list_parms()
        if isinstance(self.b, Opp):
            parms = parms + self.b.list_parms()
        return parms