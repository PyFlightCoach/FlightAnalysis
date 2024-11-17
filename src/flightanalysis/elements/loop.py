from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from . import Element
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Loop(Element):
    """Create a loop element
    ke should be a number between 0 and 2*pi, or False for 0, True for np.pi/2.
    angle represents the amount of loop to perform. Can be positive to produce an outside loop if ke==0.
    """

    parameters: ClassVar[list[str]] = (
        Element.parameters + "radius,angle,roll,ke,rate".split(",")
    )
    angle: float
    radius: float
    roll: float
    ke: float

    def describe(self):
        d1 = "loop" if self.roll == 0 else "rolling loop"
        return f"{d1}, radius = {self.radius} m, rolls = {self.roll}"

    @property
    def diameter(self):
        return self.radius * 2

    @property
    def rate(self):
        return self.roll * self.speed / (self.angle * self.radius)

    def create_template(self, istate: State, fl: State = None) -> State:
        """Generate a template loop.

        Args:
            istate (State): initial state

        Returns:
            [State]: flight data representing the loop
        """
        duration = self.radius * abs(self.angle) / self.speed

        if self.angle == 0:
            raise NotImplementedError()

        v = g.PX(self.speed) if istate.vel == 0 else istate.vel.scale(self.speed)

        return self._add_rolls(
            istate.copy(
                vel=v,
                rvel=g.Point(0, np.cos(self.ke), np.sin(self.ke)) * self.angle / duration,
            ).fill(Element.create_time(duration, fl)),
            self.roll,
        )

    def measure_radius(self, itrans: g.Transformation, flown: State):
        """The radius vector in m given a state in the loop coordinate frame"""
        centre = flown.arc_centre()

        wvec = itrans.att.transform_point(g.Point(0, np.cos(self.ke), np.sin(self.ke)))
        bvec = flown.att.inverse().transform_point(wvec)
        return abs(g.point.vector_rejection(centre, bvec))

    def weighted_average_radius(self, itrans: g.Transformation, flown: State) -> float:
        rads = self.measure_radius(itrans, flown)
        angles = np.arctan(abs(flown.vel) * flown.dt / rads)
        keep = ~np.isnan(rads * angles)

        return np.sum((rads * angles)[keep]) / np.sum(angles[keep])
        #return np.mean(rads)

    def match_intention(self, itrans: g.Transformation, flown: State) -> Loop:
        wrv = flown.att.transform_point(g.point.vector_rejection(flown.rvel, g.PX()))
        itrv = itrans.att.inverse().transform_point(wrv)
        itr = itrv.z * np.sin(self.ke) + itrv.y * np.cos(self.ke)

        return self.set_parms(
            radius=self.weighted_average_radius(itrans, flown),
            roll=abs(self.roll) * np.sign(np.mean(flown.p)),
            angle=abs(self.angle) * np.sign(itr.mean()),
            speed=abs(flown.vel).mean(),
        )

    def segment(self, transform: g.Transformation, flown: State, partitions=10):
        subsections = flown.segment(partitions)
        elms = [self.match_intention(transform, sec) for sec in subsections]

        return subsections, elms

    def copy_direction(self, other) -> Loop:
        return self.set_parms(
            roll=abs(self.roll) * np.sign(other.roll),
            angle=abs(self.angle) * np.sign(other.angle),
        )

#    def radius_visibility(self, st: State):
#        axial_dir = st[0].att.transform_point(
#            Point(0, np.cos(self.ke), np.sin(self.ke))
#        )
#        return Measurement._rad_vis(st.pos.mean(), axial_dir)


def KELoop(*args, **kwargs):
    return Loop(*args, ke=True, **kwargs)
