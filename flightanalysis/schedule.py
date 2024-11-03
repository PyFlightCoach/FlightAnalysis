from __future__ import annotations
from . import Manoeuvre
from geometry import Transformation, PX
from flightdata import State, Collection
from typing import Tuple


class Schedule(Collection):
    VType = Manoeuvre

    def create_template(self, itrans: Transformation, aligned: State=None) -> State:
        """Create labelled template flight data
        Args:
            itrans (Transformation): transformation to initial position and orientation 
        Returns:
            State: labelled template flight data
        """
        templates = [State.from_transform(itrans, vel=PX(self[0].elements[0].speed))]

        for m in self:
            templates.append(m.create_template(templates[-1][-1],aligned))

        return State.stack(templates[1:])

    def match_intention(self, itrans:Transformation, alinged: State) -> Tuple[Schedule, State]:
        """resize every element of the schedule to best fit the corresponding element in a labelled State

        Args:
            itrans (Transformation): Transformation to first point of template 
            alinged (State): labelled flight data

        Returns:
            Schedule: new schedule with all the elements resized
        """
        schedule = Schedule()
        _templates = [State.from_transform(
            Transformation(alinged[0].pos,itrans.att), 
            vel=PX(self[0].elements[0].speed)
        )]
        for man in self:
            man, template = man.match_intention(
                _templates[-1], 
                man.get_data(alinged)
            )
            schedule.add(man)
            _templates.append(template)

        return schedule, State.stack(_templates)

    def copy_directions(self, other):
        return Schedule([ms.copy_directions(mo) for ms, mo in zip(self, other)])
