from . import Manoeuvre
from typing import List


class Categories():
    F3A = 0
    IMAC = 1
    IAC = 2

    lookup = {
        "F3A": F3A,
        "IMAC": IMAC,
        "IAC": IAC
    }


class Schedule():
    def __init__(self, name: str, category: int, entry: str, manoeuvres: List[Manoeuvre]):
        self.name = name
        self.category = category
        self.entry = entry
        self.manoeuvres = manoeuvres

    @staticmethod
    def from_dict(val):
        return Schedule(
            val['name'],
            Categories.lookup[val['category']],
            val['entry'],
            [Manoeuvre.from_dict(manoeuvre) for manoeuvre in val['manoeuvres']]
        )