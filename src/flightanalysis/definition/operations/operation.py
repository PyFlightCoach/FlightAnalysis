from __future__ import annotations
from numbers import Number
from flightdata import Collection, State
from uuid import uuid1
from ast import literal_eval
from dataclasses import dataclass
from typing import Callable
import numpy as np
import re

constants = dict(
    pi=np.pi,
    c45=np.cos(np.radians(45)),
)

def check_constant(inp:str):
    if inp in constants:
        return constants[inp]
    else:
        raise ValueError(f"Unknown constant {inp}")


def bracksplit(data: str):
    outarr = [""]

    for val in data.split(","):
        outarr[-1] = f"{outarr[-1]},{val}"
        opencount = len(re.findall(r"\(", outarr[-1]))
        closecount = len(re.findall(r"\)", outarr[-1]))
        if opencount == closecount:
            outarr.append("")

    return [o[1:] for o in outarr[:-1]]


@dataclass
class Opp:
    __array_priority__ = 15.0
    name: str
    
    def __getattr__(self, name):
        if name == "name":
            self.name = uuid1() 
            return self.name

    def __str__(self):
        return self.name 

    def get_vf(self, arg):
        """create a function that returns the value, given the manparms"""
        if isinstance(arg, Opp):
            return arg
        elif isinstance(arg, Number):
            return lambda *args, **kwargs: arg
        else:
            raise AttributeError("expected a number or an Opp")

    def __abs__(self) -> FunOpp:
        return FunOpp(self.name, "abs", self)

    def sign(self) -> FunOpp:
        return FunOpp(self.name, "abs", self)

    def __add__(self, other) -> MathOpp:
        return MathOpp(self.name, self, other, "+")

    def __radd__(self, other) -> MathOpp:
        return MathOpp(self.name, other, self, "+")

    def __mul__(self, other) -> MathOpp:
        return MathOpp(self.name, self, other, "*")

    def __rmul__(self, other) -> MathOpp:
        return MathOpp(self.name, other, self, "*")

    def __sub__(self, other) -> MathOpp:
        return MathOpp(self.name, self, other, "-")

    def __rsub__(self, other) -> MathOpp:
        return MathOpp(self.name, other, self, "-")

    def __div__(self, other) -> MathOpp:
        return MathOpp(self.name, self, other, "/")

    def __rdiv__(self, other) -> MathOpp:
        return MathOpp(self.name, other, self, "/")

    def __truediv__(self, other) -> MathOpp:
        return MathOpp(self.name, self, other, "/")

    def __rtruediv__(self, other) -> MathOpp:
        return MathOpp(self.name, other, self, "/")

    def __getitem__(self, i) -> ItemOpp:
        return ItemOpp(self.name, self, i)


    @staticmethod
    def parse(inp, coll:Collection | Callable, name=None):
        """Parse an Operation from a string"""
        if isinstance(inp, Number) or isinstance(inp, Opp):
            return inp 
        inp = inp.strip(" ")
        for test in [
            lambda inp : float(inp),
            lambda inp : check_constant(inp),
            lambda inp : FunOpp.parse(inp, coll, name),
            lambda inp : MathOpp.parse(inp, coll, name),
            lambda inp : ItemOpp.parse(inp, coll, name),
            lambda inp : SumOpp.parse(inp, coll, name),
            lambda inp : literal_eval(inp)
        ]:
            try:
                return test(inp)
            except ValueError:
                continue
        else:
            return coll[inp] if isinstance(coll, Collection) else coll(inp)

    def list_parms(self) -> list[str]:
        return []
    
    def extract_state(self, els, st: State):
        elnames = list(set([parm.elname for parm in self.list_parms()]))

        return State.stack([els.data[elname].get_data(st) for elname in elnames])


from .mathopp import MathOpp  # noqa: E402
from .funopp import FunOpp, maxopp, minopp  # noqa: E402
from .itemopp import ItemOpp  # noqa: E402
from .sumopp import SumOpp  # noqa: E402