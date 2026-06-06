from __future__ import annotations
from dataclasses import dataclass, replace
from flightdata.base import Collection
from flightdata import State
from flightanalysis.base.utils import parse_csv
from flightanalysis.elements import AnyElement
from .link_conditions import conditions as lcons, Condition


@dataclass
class Linker:
    name: str
    dg1: list[str]
    dg2: list[str]
    conditions: dict[str, Condition]

    def check(
        self, el1: AnyElement, tp1: State, el2: AnyElement, tp2: State
    ) -> bool:
        return all(
            condition(el1, tp1, el2, tp2)
            for condition in self.conditions.values()
        )


class Linkers(Collection[Linker]):
    uid = "name"

    def find_linker(self, dg1: str, dg2: str) -> Linker:
        try:
            return self.filter_values(
                lambda linker: dg1 in linker.dg1 and dg2 in linker.dg2
            )[0]
        except IndexError:
            return None

    @staticmethod
    def from_csv(path: str) -> Linkers:
        df = parse_csv(path, sep=";")
        linkers = []
        for k, r in df.iterrows():
            _conditions = [c.strip() for c in r["Conditions"].split(",")]

            linkers.append(
                Linker(
                    name=r["name"].strip(),
                    dg1=[e.strip() for e in r["dg1"].split(",")],
                    dg2=[e.strip() for e in r["dg2"].split(",")],
                    conditions={c: lcons[c] for c in _conditions if c in lcons},
                )
            )
        return Linkers(linkers)
