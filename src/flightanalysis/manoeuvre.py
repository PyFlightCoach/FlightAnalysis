from __future__ import annotations
import geometry as g
from typing import Tuple, Literal, Self
from dataclasses import dataclass
from flightdata.state import State
from flightanalysis.elements import Elements, Element, Line


@dataclass
class Manoeuvre:
    elements: Elements  # now always includes the entry line and the exit line
    uid: str = None

    def __post_init__(self):
        assert self.elements[0].uid == "entry_line", "First element must be an entry line"
        assert self.elements[-1].uid == "exit_line", "Last element must be an exit line"

    @staticmethod
    def from_dict(data) -> Manoeuvre:
        return Manoeuvre(
            Elements.from_dicts(data["elements"]),
            data["uid"],
        )

    def to_dict(self):
        return dict(
            elements=self.elements.to_dicts(),
            uid=self.uid,
        )

    def create_template(
        self,
        initial: g.Transformation | State,
        aligned: State = None,
        freq: int = 20,
        npoints: int | Literal["min"] = 3,
    ) -> dict[str, State]:
        return self.elements.create_templates(initial, aligned, freq, npoints)

    def match_intention(
        self,
        istate: State | g.Transformation,
        aligned: State,
        freq: int = 20,
        npoints: int | Literal["min"] = 2,
        match_index: bool = True
    ) -> Tuple[Self, dict[str, State]]:
        """Create a new manoeuvre with all the elements scaled to match the corresponding
        flown element"""
        elms, tpdict = self.elements.match_intention(
            istate, aligned, freq, npoints, match_index
        )

        return Manoeuvre(elms, self.uid), tpdict

    def copy(self):
        return Manoeuvre(
            self.uid, self.elements.copy(deep=True)
        )

    def copy_directions(self, other: Manoeuvre) -> Self:
        return Manoeuvre(
            self.elements.copy_directions(other.elements),
            self.uid
            )
        

    def descriptions(self):
        return [e.describe() for e in self.elements]

    def __repr__(self):
        return f"Manoeuvre({self.uid}, len={len(self.elements)})"
