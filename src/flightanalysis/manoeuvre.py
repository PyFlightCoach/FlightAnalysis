from __future__ import annotations
import geometry as g
from typing import Tuple, Literal, Self
from dataclasses import dataclass
from flightdata.state import State
from flightanalysis.elements import Elements, Element, Line


@dataclass
class Manoeuvre:
    elements: Elements  # now always includes the entry line
    exit_line: Line
    uid: str = None

    @staticmethod
    def from_dict(data) -> Manoeuvre:
        return Manoeuvre(
            Elements.from_dicts(data["elements"]),
            Line.from_dict(data["exit_line"]) if data["exit_line"] else None,
            data["uid"],
        )

    def to_dict(self):
        return dict(
            elements=self.elements.to_dicts(),
            exit_line=self.exit_line.to_dict() if self.exit_line else None,
            uid=self.uid,
        )

    @staticmethod
    def from_all_elements(uid: str, els: list[Element]) -> Manoeuvre:
        hasexit = -1 if els[-1].uid.startswith("exit_") else None

        return Manoeuvre(
            Elements(els[0:hasexit]),
            els[-1] if hasexit else None,
            uid,
        )

    def all_elements(self, create_exit: bool = False) -> Elements:
        els = Elements()

        els.add(self.elements)

        if self.exit_line:
            els.add(self.exit_line)
        elif create_exit:
            els.add(Line("exit_line", self.elements[0].speed, 30, 0))

        return els

    def add_lines(self, add_entry=True, add_exit=True) -> Manoeuvre:
        return Manoeuvre.from_all_elements(self.uid, self.all_elements(add_exit))

    def remove_exit_line(self) -> Manoeuvre:
        return Manoeuvre(
            self.elements,
            None,
            self.uid,
        )

    def create_template(
        self,
        initial: g.Transformation | State,
        aligned: State = None,
        freq: int = 25,
        npoints: int | Literal["min"] = 3,
    ) -> dict[str, State]:
        return self.all_elements().create_templates(initial, aligned, freq, npoints)

    def match_intention(
        self,
        istate: State | g.Transformation,
        aligned: State,
        freq: int = 30,
        npoints: int | Literal["min"] = 2,
        match_index: bool = True
    ) -> Tuple[Self, dict[str, State]]:
        """Create a new manoeuvre with all the elements scaled to match the corresponding
        flown element"""
        elms, tpdict = self.all_elements().match_intention(
            istate, aligned, freq, npoints, match_index
        )

        return Manoeuvre.from_all_elements(self.uid, elms), tpdict

    def copy(self):
        return Manoeuvre.from_all_elements(
            self.uid, self.all_elements().copy(deep=True)
        )

    def copy_directions(self, other: Manoeuvre) -> Self:
        return Manoeuvre.from_all_elements(
            self.uid,
            Elements(self.all_elements().copy_directions(other.all_elements())),
        )

    def descriptions(self):
        return [e.describe() for e in self.elements]

    def __repr__(self):
        return f"Manoeuvre({self.uid}, len={len(self.elements)})"
