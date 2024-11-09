
from __future__ import annotations
from flightdata import Collection
from dataclasses import dataclass
from typing import Callable
from .operation import Opp
from .funopp import FunOpp


@dataclass
class ItemOpp(Opp):
    """This class creates an Operation that returns a single item,
        usually from a Combination manparm"""
    a: Opp
    item: int
    
    def __call__(self, mps, **kwargs):
        return mps.data[self.a.name].value[self.item]
    
    def __str__(self):
        return f"{self.a.name}[{self.item}]"

    @staticmethod
    def parse(inp: str, coll: Collection | Callable, name:str=None):
        if not inp.endswith("]"):
            raise ValueError("ItemOpp must be in the form of 'a[item]'")
        contents = inp[:-1].rsplit("[", 1)
        if not len(contents) == 2:
            raise ValueError
        return ItemOpp(
            name,
            Opp.parse(contents[0], coll, name), 
            int(contents[1])
        )

    def __abs__(self):
        return FunOpp(self.name, self, "abs")

    def list_parms(self):
        if isinstance(self.a, Opp):
            return self.a.list_parms()
        else:
            return []