from __future__ import annotations
from geometry import Transformation, PX
from typing import  Tuple, Self
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
    ) -> dict[str, State]:
        istate = (
            State.from_transform(initial, vel=PX())
            if isinstance(initial, Transformation)
            else initial
        )
        templates = [istate]
        for i, element in enumerate(self.all_elements()):
            templates.append(
                element.create_template(
                    templates[-1][-1], aligned.element[element.uid] if aligned else None
                )
            )

        return {el.uid: tp for el, tp in zip(self.all_elements(), templates[1:])}

    def match_intention(self, istate: State, aligned: State) -> Tuple[Self, dict[str, State]]:
        """Create a new manoeuvre with all the elements scaled to match the corresponding
        flown element"""

        elms = Elements()
        templates = [istate]
        
        for elm in self.all_elements():
            st = aligned.element[elm.uid]
            elms.add(elm.match_intention(templates[-1][-1].transform, st))

            templates.append(elms[-1].create_template(templates[-1][-1], st))

        return Manoeuvre.from_all_elements(self.uid, elms), {el.uid: tp for el, tp in zip(elms, templates[1:])} 
     #State.stack(
     #       templates[1:], "element", [el.uid for el in elms]
     #   )

    def el_matched_tp(self, istate: State, aligned: State) -> dict[str, State]:
        aligned = self.get_data(aligned)
        templates = [istate]
        for el in self.all_elements():
            st = aligned.element[el.uid]
            templates.append(el.create_template(templates[-1][-1], st))
        return {el.uid: tp for el, tp in zip(self.all_elements(), templates[1:])}

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
