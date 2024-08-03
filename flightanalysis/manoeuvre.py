from __future__ import annotations
from geometry import Transformation, PX
from typing import List, Union, Tuple, Self
import numpy as np
from dataclasses import dataclass
from flightdata.state import State
from flightanalysis.elements import Elements, Element, Line, Autorotation


@dataclass
class Manoeuvre:
    entry_line: Line
    elements: Elements
    exit_line: Line
    uid: str = None

    @staticmethod
    def from_dict(data) -> Manoeuvre:
        return Manoeuvre(
            Line.from_dict(data["entry_line"]) if data["entry_line"] else None,
            Elements.from_dicts(data["elements"]),
            Line.from_dict(data["exit_line"]) if data["exit_line"] else None,
            data["uid"],
        )

    def to_dict(self):
        return dict(
            entry_line=self.entry_line.to_dict(exit_only=True)
            if self.entry_line
            else None,
            elements=self.elements.to_dicts(),
            exit_line=self.exit_line.to_dict() if self.exit_line else None,
            uid=self.uid,
        )

    @staticmethod
    def from_all_elements(uid: str, els: List[Element]) -> Manoeuvre:
        hasentry = 1 if els[0].uid.startswith("entry_") else None
        hasexit = -1 if els[-1].uid.startswith("exit_") else None

        return Manoeuvre(
            els[0] if hasentry else None,
            els[hasentry:hasexit],
            els[-1] if hasexit else None,
            uid,
        )

    def all_elements(
        self, create_entry: bool = False, create_exit: bool = False
    ) -> Elements:
        els = Elements()

        if self.entry_line:
            els.add(self.entry_line)
        elif create_entry:
            els.add(Line("entry_line", self.elements[0].speed, 30, 0))

        els.add(self.elements)

        if self.exit_line:
            els.add(self.exit_line)
        elif create_exit:
            els.add(Line("exit_line", self.elements[0].speed, 30, 0))

        return els

    def add_lines(self, add_entry=True, add_exit=True) -> Manoeuvre:
        return Manoeuvre.from_all_elements(
            self.uid, self.all_elements(add_entry, add_exit)
        )

    def remove_lines(self, remove_entry=True, remove_exit=True) -> Manoeuvre:
        return Manoeuvre(
            None if remove_entry else self.entry_line,
            self.elements,
            None if remove_exit else self.exit_line,
            self.uid,
        )

    def create_template(
        self, initial: Union[Transformation, State], aligned: State = None
    ) -> State:
        istate = (
            State.from_transform(initial, vel=PX())
            if isinstance(initial, Transformation)
            else initial
        )
        aligned = self.get_data(aligned) if aligned else None
        templates = []
        els = self.all_elements()
        for i, element in enumerate(els):
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
        els = self.all_elements()
        for i, elm in enumerate(els):
            st = elm.get_data(aligned)
            elms.add(elm.match_intention(templates[-1][-1].transform, st))

            if isinstance(elms[-1], Autorotation):
                # copy the autorotation pitch offset back to the preceding pitch departure
                angles = np.arctan2(st.vel.z, st.vel.x)
                pos_break = max(angles)
                neg_break = min(angles)
                elms[-2].break_angle = (
                    pos_break if pos_break > -neg_break else neg_break
                )

            templates.append(
                elms[-1].create_template(templates[-1][-1],  st)
            )

        return Manoeuvre.from_all_elements(self.uid, elms), State.stack(
            templates[1:]
        ).label(manoeuvre=self.uid)

    def el_matched_tp(self, istate: State, aligned: State) -> State:
        els = self.all_elements()
        aligned = self.get_data(aligned)
        templates = [istate]
        for i, el in enumerate(els):
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
