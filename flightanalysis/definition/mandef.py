"""This module contains the structures used to describe the elements within a manoeuvre and
their relationship to each other. 

A Manoeuvre contains a dict of elements which are constructed in order. The geometry of these
elements is described by a set of high level parameters, such as loop radius, combined line 
length of lines, roll direction. 

A complete manoeuvre description includes a set of functions to create the elements based on
the higher level parameters and another set of functions to collect the parameters from the 
elements collection.

"""
from __future__ import annotations
import numpy as np
from flightanalysis.elements import Line, Elements
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.definition.maninfo import ManInfo
from flightdata import State
from geometry import Transformation, Euler, Point
from . import ManParms, ElDef, ElDefs, Position, Direction


class ManDef:
    """This is a class to define a manoeuvre for template generation and judging.

    It also contains lots of helper functions for creating elements and common combinations
    of elements.
    """

    def __init__(self, info: ManInfo, mps: ManParms = None, eds: ElDefs = None):
        self.info: ManInfo = info
        self.mps: ManParms = ManParms.create_defaults_f3a() if mps is None else mps
        self.eds: ElDefs = ElDefs() if eds is None else eds

    @property
    def uid(self):
        return self.info.short_name

    def to_dict(self):
        return dict(
            info = self.info.to_dict(),
            mps = self.mps.to_dict(),
            eds = self.eds.to_dict()
        )

    @staticmethod
    def from_dict(data: dict) -> ManDef:
        info = ManInfo.from_dict(data["info"])
        mps = ManParms.from_dict(data["mps"])
        eds = ElDefs.from_dict(data["eds"], mps)
        return ManDef(info, mps, eds)

    def create_entry_line(self, itrans: Transformation=None, target_depth=170) -> ElDef:
        """Create a line definition connecting Transformation to the start of this manoeuvre.

        The length of the line is set so that the manoeuvre is centred or extended to box
        edge as required.

        Args:
            itrans (Transformation): The location to draw the line from, usually the end of the last manoeuvre.

        Returns:
            ElDef: A Line element that will position this manoeuvre correctly.
        """
        itrans = self.info.initial_transform(170, 1) if itrans is None else itrans
                
        heading = np.sign(itrans.rotation.transform_point(Point(1, 0, 0)).x[0]) # 1 for +ve x heading, -1 for negative x

        #Create a template at zero to work out how much space the manoueuvre needs
        man = self._create()
        template = man.create_template(
            State.from_transform(Transformation(
                Point(0,0,0),
                Euler(self.info.start.o.roll_angle(), 0, 0)
        )))
          
        if self.info.start.d == Direction.CROSS:
            st = State.from_transform(itrans)
            man_l = template.x[-1] - template.x[0]
            length = max(target_depth - man_l * st.cross_direction() - st.pos.y[0], 30)
        else:
            if self.info.position == Position.CENTRE:
                if len(self.info.centre_points) > 0:
                    man_start_x = -man.elements[self.info.centre_points[0]].get_data(template).pos.x[0]
                elif len(self.info.centred_els) > 0:
                    ce, fac = self.info.centred_els[0]
                    _x = man.elements[ce].get_data(template).pos.x
                    man_start_x = -_x[int(len(_x) * fac)]
                else:
                    man_start_x = -(max(template.pos.x) + min(template.pos.x))/2
                    
            elif self.info.position ==  Position.END:
                    box_edge = np.tan(np.radians(60)) * (np.abs(template.pos.y) + itrans.pos.y[0])
                    man_start_x = min(box_edge - template.pos.x) 
            length = max(man_start_x - itrans.translation.x[0] * heading, 30)

        return ElDef.build(Line, "entry_line", 30.0, length, 0)

    def create(self, itrans=None, depth=None, wind=None, cross=None) -> Manoeuvre:
        """Create the manoeuvre based on the default values in self.mps.

        Returns:
            Manoeuvre: The manoeuvre
        """
        try:
            return Manoeuvre(
                self.create_entry_line(
                    self.info.initial_transform(depth, wind, cross) if itrans is None else itrans
                )(self.mps),
                Elements([ed(self.mps) for ed in self.eds]), 
                None,
                uid=self.info.short_name
            )
        except Exception as e:
            raise Exception(f"Error creating manoeuvre {self.info.short_name} due to: {e}") from e
    def _create(self) -> Manoeuvre:
        return Manoeuvre(
            None,
            Elements([ed(self.mps) for ed in self.eds]),
            None,
            uid=self.info.name
        ) 

    def plot(self):
        itrans = self.info.initial_transform(170, 1)
        man = self.create(itrans)
        template = man.create_template(itrans)
        from flightplotting import plotsec, plotdtw
        fig = plotdtw(template, template.data.element.unique())
        fig = plotsec(template, fig=fig, nmodels=20, scale=3)
        return fig
