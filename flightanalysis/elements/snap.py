from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from .element import Element
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Snap(Element):
    parameters: ClassVar[list[str]] = Element.parameters + [
        "length",
        "roll",
        "pitch",
        "break_roll",
        "recovery_roll",
        "rate",
    ]

    length: float
    roll: float
    pitch: float
    break_roll: float
    recovery_roll: float

    @property
    def rate(self):
        return (
            (abs(self.roll) + self.break_roll + self.recovery_roll)
            * self.speed
            / self.length
        )

    def get_length(speed, rate, roll, break_roll, recovery_roll):
        return speed * (abs(roll) + break_roll + recovery_roll) / rate

    def create_template(self, istate: State, fl: State = None) -> State:
        
        world_rot_axis = istate.att.transform_point(g.PX())
        rate = self.rate
        ttot = self.length / self.speed

        _tpb = 2 * abs(self.break_roll) / rate
        tpb = g.Time.uniform(_tpb, int(np.ceil(len(fl) * _tpb / ttot)) if fl else None, 2)

        _trec = 2 * abs(self.recovery_roll) / rate
        trec = g.Time.uniform(_trec, int(np.ceil(len(fl) * _trec / ttot)) if fl else None, 2)

        _tau = ttot * abs((abs(self.roll) - self.break_roll - self.recovery_roll) / self.roll)
        tau = g.Time.uniform(_tau, len(fl) - len(tpb) - len(trec) + 2  if fl else None, 2)

        pb = (
            istate.copy(vel=g.PX(self.speed), rvel=g.P0())
            .fill(tpb)
            .superimpose_rotation(g.PY(), self.pitch)
            .superimpose_angles(
                np.sign(self.roll) * world_rot_axis * rate * tpb.t**2 / (2 * tpb.t[-1]),
                reference="world",
            )
        )

        au: State = (
            pb[-1]
            .copy(rvel=g.P0())
            .fill(tau)
            .superimpose_rotation(
                world_rot_axis,
                np.sign(self.roll)
                * (abs(self.roll) - self.break_roll - self.recovery_roll),
                "world",
            )
        )

        rec: State = (
            au[-1]
            .copy(rvel=g.P0())
            .fill(trec)
            .superimpose_rotation(g.PY(), -self.pitch)
            .superimpose_angles(
                np.sign(self.roll)
                * world_rot_axis
                * rate
                * (trec.t - 0.5 * trec.t**2 / trec.t[-1]),
                reference="world",
            )
        )

        return State.stack([pb, au, rec]).label(element=self.uid)
        # .superimpose_rotation(
        #    istate.att.transform_point(g.PX()), self.roll, reference="world"
        # )

    def describe(self):
        return f"Snap {self.roll}, {self.pitch}"

    def match_intention(self, transform: g.Transformation, flown: State) -> Snap:
        snap_rate = g.Point.scalar_projection(flown.rvel, flown.vel)

        snap_angle = np.cumsum(snap_rate * flown.dt)

        ipb = np.where(np.abs(snap_angle) > self.break_roll)[0][0]
        irec = np.where(np.abs(snap_angle) < (np.abs(self.roll) - self.recovery_roll))[
            0
        ][-1]
        autorot_rate = np.mean(snap_rate[ipb:irec])
        speed = np.mean(abs(flown.vel))
        pitch = np.arctan2(flown.vel.z, flown.vel.x)

        return self.set_parms(
            length=Snap.get_length(
                speed, abs(autorot_rate), self.roll, self.break_roll, self.recovery_roll
            ),
            roll=np.sign(autorot_rate) * abs(self.roll),
            speed=speed,
            pitch=np.mean(pitch[ipb:irec] - pitch[0]),
        )
