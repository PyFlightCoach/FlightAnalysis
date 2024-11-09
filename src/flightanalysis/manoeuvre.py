from __future__ import annotations
from geometry import Transformation, PX
from typing import List, Union, Tuple, Self
import numpy as np
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
    def from_all_elements(uid: str, els: List[Element]) -> Manoeuvre:
        hasexit = -1 if els[-1].uid.startswith("exit_") else None

        return Manoeuvre(
            els[0:hasexit],
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
        return Manoeuvre.from_all_elements(
            self.uid, self.all_elements(add_exit)
        )

    def remove_exit_line(self) -> Manoeuvre:
        return Manoeuvre(
            self.elements,
            None,
            self.uid,
        )

    def create_template(
        self, initial: Transformation | State, aligned: State = None
    ) -> State:
        istate = (
            State.from_transform(initial, vel=PX())
            if isinstance(initial, Transformation)
            else initial
        )
        aligned = self.get_data(aligned) if aligned else None
        templates = []
        for i, element in enumerate(self.all_elements()):
            templates.append(
                element.create_template(
                    istate, element.get_data(aligned) if aligned else None
                )
            )
            istate = templates[-1][-1]

        return State.stack(templates).label(manoeuvre=self.uid)

    def get_data(self, st: State) -> State:
        return st.get_manoeuvre(self.uid)

    def match_intention(self, istate: State, aligned: State) -> Tuple[Self, State]:
        """Create a new manoeuvre with all the elements scaled to match the corresponding
        flown element"""

        elms = Elements()
        templates = [istate]
        aligned = self.get_data(aligned)
        
        for elm in self.all_elements():
            st = elm.get_data(aligned)
            elms.add(elm.match_intention(templates[-1][-1].transform, st))

            templates.append(elms[-1].create_template(templates[-1][-1], st))

        return Manoeuvre.from_all_elements(self.uid, elms), State.stack(
            templates[1:]
        ).label(manoeuvre=self.uid)

    def el_matched_tp(self, istate: State, aligned: State) -> State:
        aligned = self.get_data(aligned)
        templates = [istate]
        for el in self.all_elements():
            st = el.get_data(aligned)
            templates.append(el.create_template(templates[-1][-1], st))
        return State.stack(templates[1:])

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
