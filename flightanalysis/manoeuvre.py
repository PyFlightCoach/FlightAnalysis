from __future__ import annotations
from geometry import Transformation, PX
from typing import List, Union, Tuple, Self
import numpy as np
from dataclasses import dataclass


from flightdata.state import State
from flightanalysis.elements import Elements, Element, Line, Autorotation
from flightanalysis.scoring import *


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
            data["uid"]
        )

    def to_dict(self):
        return dict(
            entry_line=self.entry_line.to_dict(exit_only=True) if self.entry_line else None,
            elements=self.elements.to_dicts(),
            exit_line=self.exit_line.to_dict() if self.exit_line else None,
            uid=self.uid
        )

    @staticmethod
    def from_all_elements(uid:str, els: List[Element]) -> Manoeuvre:
        hasentry = 1 if els[0].uid.startswith("entry_") else None
        hasexit = -1 if els[-1].uid.startswith("exit_") else None

        return Manoeuvre(
            els[0] if hasentry else None, 
            els[hasentry:hasexit], 
            els[-1] if hasexit else None, 
            uid
        )

    def all_elements(self, create_entry: bool = False, create_exit: bool = False) -> Elements:
        els = Elements()

        if self.entry_line:
            els.add(self.entry_line)
        elif create_entry:
            els.add(Line(self.elements[0].speed, 30, 0, "entry_line"))

        els.add(self.elements)

        if self.exit_line:
            els.add(self.exit_line)
        elif create_exit:
            els.add(Line(self.elements[0].speed, 30, 0, "exit_line"))

        return els

    def add_lines(self, add_entry=True, add_exit=True) -> Manoeuvre:
        return Manoeuvre.from_all_elements(self.uid, self.all_elements(add_entry, add_exit))
    
    def remove_lines(self, remove_entry=True, remove_exit=True) -> Manoeuvre:
        return Manoeuvre(
            None if remove_entry else self.entry_line, 
            self.elements, 
            None if remove_exit else self.exit_line, 
            self.uid
        )
    
    def create_template(self, initial: Union[Transformation, State], aligned:State=None) -> State:
        
        istate = State.from_transform(initial, vel=PX()) if isinstance(initial, Transformation) else initial
        aligned = self.get_data(aligned) if aligned else None
        templates = []
        els = self.all_elements()
        for i, element in enumerate(els):
            time = element.get_data(aligned).time if not aligned is None else None

            if i < len(els)-1 and not time is None:
                time = time.extend()
            templates.append(element.create_template(istate, time))
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
                #copy the autorotation pitch offset back to the preceding pitch departure
                angles = np.arctan2(st.vel.z, st.vel.x)
                pos_break = max(angles)
                neg_break = min(angles)
                elms[-2].break_angle = pos_break if pos_break > -neg_break else neg_break
                
            templates.append(elms[-1].create_template(
                templates[-1][-1].relocate(st[0].pos), 
                st.time.extend() if i < len(els) - 1 else st.time
            ))
                    
        return Manoeuvre.from_all_elements(self.uid, elms), State.stack(templates[1:]).label(manoeuvre=self.uid)

    def el_matched_tp(self, istate: State, aligned: State) -> State:
        els = self.all_elements()
        aligned= self.get_data(aligned)
        templates = [istate]
        for i, el in enumerate(els):
            st = el.get_data(aligned)
            templates.append(el.create_template(
                templates[-1][-1].relocate(st[0].pos), 
                st.time.extend() if i < len(els) - 1 else st.time
            ))
        return State.stack(templates[1:])

    def copy(self):
        return Manoeuvre.from_all_elements(self.uid, self.all_elements().copy(deep=True))

    def copy_directions(self, other: Manoeuvre) -> Self:
        return Manoeuvre.from_all_elements(
            self.uid, 
            Elements(self.all_elements().copy_directions(other.all_elements()))
        )

    def analyse(self, flown: State, template: State):
        fl=self.entry_line.get_data(flown)
        tp=self.entry_line.get_data(template).relocate(fl.pos[0])
        
        ers = [Results(self.entry_line.uid, self.entry_line.analyse_exit(fl, tp))]

        for el in self.elements:
            fl = el.get_data(flown)
            tp = el.get_data(template).relocate(fl.pos[0])
            ers.append(Results(el.uid, el.analyse(fl, tp)))
        return ElementsResults(ers)

    def optimise_alignment(self, istate: State, aligned: State) -> Tuple(Self, State):
        els = self.all_elements()
        elns = list(els.data.keys())
        
        for eln1, eln2 in zip(elns[:-1], elns[1:]):
            fl1, fl2 = aligned.get_element(eln1), aligned.get_element(eln2)
            steps = Element.optimise_split(istate, els[eln1], els[eln2], fl1, fl2)
            if not steps == 0:
                aligned = aligned.shift_label(steps, 2, manoeuvre=self.uid, element=eln1)
            istate = els[eln1].create_template(istate)[-1]
        
        return aligned

    
    def descriptions(self):
        return [e.describe() for e in self.elements]
    
    def __repr__(self):
        return f'Manoeuvre({self.uid}, len={len(self.elements)})'