from __future__ import annotations
from numbers import Number
from flightdata import Collection
from uuid import uuid1
from ast import literal_eval
from dataclasses import dataclass


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

    def __call__(self, coll, **kwargs):
        return self.value

    def get_vf(self, arg):
        if isinstance(arg, Opp):
            return arg
        elif isinstance(arg, Number):
            return lambda mps, **kwargs: arg


    def __abs__(self) -> FunOpp:
        return FunOpp(self.name, self, "abs")

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

    def __abs__(self) -> MathOpp:
        return FunOpp(self.name, self, "abs")

    def __getitem__(self, i) -> ItemOpp:
        return ItemOpp(self.name, self, i)

    @staticmethod
    def parse_f(inp, parser, name=None):
        """Parse a an Operation from a string"""
        for test in [
            lambda inp : float(inp),
            lambda inp : FunOpp.parse_f(inp, parser, name),
            lambda inp : MathOpp.parse_f(inp, parser, name),
            lambda inp : ItemOpp.parse_f(inp, parser, name),
            lambda inp : literal_eval(inp)
        ]: 
            try: 
                return test(inp.strip(" "))
            except ValueError:
                continue
        else:
            return parser(inp)

    @staticmethod
    def parse(inp, coll:Collection, name=None):
        """Parse a an Operation from a string
        TODO move to the subclass and call parse_f"""
        for test in [
            lambda inp, mps : float(inp),
            lambda inp, mps : FunOpp.parse(inp, coll, name),
            lambda inp, mps : MathOpp.parse(inp, coll, name),
            lambda inp, mps : ItemOpp.parse(inp, coll, name),
            lambda inp, mps : literal_eval(inp)
        ]:
            if isinstance(inp, Number) or isinstance(inp, Opp):
                return inp 
            try: 
                return test(inp.strip(" "), coll)
            except ValueError:
                continue
        else:
            return coll[inp]

from .mathopp import MathOpp
from .funopp import FunOpp
from .itemopp import ItemOpp