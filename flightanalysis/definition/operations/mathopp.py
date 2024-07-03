from __future__ import annotations
from flightdata import Collection
from dataclasses import dataclass
from numbers import Number
from .operation import Opp


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
    def parse_f(inp:str, parser, name:str=None):
        if inp.startswith("(") and inp.endswith(")"):
            bcount = 0
            for i, l in enumerate(inp):
                bcount += 1 if l=="(" else 0
                bcount -=1 if l==")" else 0
            
                if bcount == 1 and l in oplu.keys():
                    return MathOpp(
                        name,
                        Opp.parse_f(inp[1:i], parser, name),
                        Opp.parse_f(inp[i+1:-1], parser, name),
                        l
                    )
                    
        raise ValueError(f"cannot read an MathOpp from the outside of {inp}")

    @staticmethod
    def parse(inp:str, coll: Collection, name:str=None):
        if inp.startswith("(") and inp.endswith(")"):
            bcount = 0
            for i, l in enumerate(inp):
                bcount += 1 if l=="(" else 0
                bcount -=1 if l==")" else 0
            
                if bcount == 1 and l in oplu.keys():
                    return MathOpp(
                        name,
                        coll.VType.parse(inp[1:i], coll),
                        coll.VType.parse(inp[i+1:-1], coll),
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