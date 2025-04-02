from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from .element import Element
from dataclasses import dataclass
from typing import ClassVar
from pudb import set_trace


@dataclass
class Spin(Element):
    parameters: ClassVar[list[str]] = Element.parameters + [
        "height",
        "turns",
        "rturns",
        "pitch",
        "drop_turns",
        "recovery_turns",
        "reversal_turns",
        "rate"
    ]
    # reversal_turns - slowing autorotation before rotating in reverse = starting reverse auto
    height: float
    turns: float  # sounds strange but this is in radians
    rturns: float 
    pitch: float
    drop_turns: float  # radians
    recovery_turns: float  # radians
    reversal_turns: float  # radians

    @property
    def length(self):
        # drop_turn + turns + recovery_turn + reversal_turn + rturns + recovery_turn
        # reversal_turn - the same length as drop_turn but attitude is the same as rturns (same rate as turns)
        # all turns are measured in radians
        return (
            (self.drop_turns + abs(self.turns) + self.recovery_turns) * self.speed / self.rate if self.rturns == 0 else 
            (self.drop_turns + abs(self.turns) + self.recovery_turns 
            + self.reversal_turns + abs(self.rturns) + self.recovery_turns ) * self.speed / self.rate
        )

    @property
    def rate(self):
        return (
            ((4 / np.pi - 1) * self.drop_turns + abs(self.turns) + self.recovery_turns) * 
            self.speed / self.height  if self.rturns == 0 else 
            ((4 / np.pi - 1) * self.drop_turns + abs(self.turns) + 
            (4 / np.pi - 1) * self.reversal_turns + abs(self.rturns) + self.recovery_turns ) * 
            self.speed / self.height
        )
        
    @staticmethod
    def get_height(
        speed: float,
        rate: float,
        turns: float,
        rturns: float,
        drop_turns: float,
        recovery_turns: float,
        reversal_turns: float
    ):
        return (
            ((4 / np.pi - 1) * drop_turns + abs(turns) + recovery_turns) * 
            speed / rate if rturns == 0 else 
            ((4 / np.pi - 1) * drop_turns + abs(turns) + 
            (4 / np.pi - 1) * reversal_turns + abs(rturns) + recovery_turns ) * 
            speed / rate
        )

    def create_template(self, istate: State, fl: State = None) -> State:
        # set_trace()
        istate = istate.copy(vel=g.PX(self.speed))
        _inverted = 1 if istate.transform.rotation.is_inverted()[0] else -1
        
        rate = self.rate * 2
        firstSpinsLength = (self.drop_turns + abs(self.turns) + self.recovery_turns) * self.speed / self.rate
        timeFirstSpins = firstSpinsLength / self.speed 

        _td = 2 * self.drop_turns / rate
        tnd = g.Time.uniform(_td, int(np.ceil(len(fl) * _td / timeFirstSpins)) if fl else None)
        
        nd: State = (
            istate.copy(
                vel=istate.vel.scale(self.speed),
                rvel=g.PY(_inverted * 0.5 * np.pi / _td),
            )
            .fill(tnd)
            .superimpose_rotation(g.PY(), -abs(self.pitch) * _inverted)
            .superimpose_angles(
                g.PZ(np.sign(self.turns)) * rate * tnd.t**2 / (2 * _td),
                reference="world",
            )
        )

        _tau = timeFirstSpins - _td
        tau = g.Time.uniform(_tau, len(fl) - len(tnd) + 2 if fl else None)
        
        _trec = 2 * self.recovery_turns / rate
        trec = g.Time.uniform(
            _trec, int(np.ceil(len(fl) * _trec / timeFirstSpins)) if fl else None
        )
        
        if (self.rturns != 0.0):
        
            au: State = (
                nd[-1]
                .copy(rvel=g.P0())
                .fill(tau)
                .label(element=self.uid + "_autorotation")
                .superimpose_rotation(
                    g.PZ(),
                    np.sign(self.turns) * (abs(self.turns) - self.drop_turns),
                    "world",
                )
            )

            reversedSpinsLength = (abs(self.rturns) + self.recovery_turns) * self.speed / self.rate
            timeReversalSpins = reversedSpinsLength / self.speed
            
            _trec = 2 * self.recovery_turns / rate
            trec = g.Time.uniform(
                _trec, int(np.ceil(len(fl) * _trec / timeReversalSpins)) if fl else None
            )
            
            _tau = timeReversalSpins - _trec
            tau = g.Time.uniform(_tau, len(fl) - len(tnd) + 2 if fl else None)

            au2: State = (
                au[-1]
                .copy(rvel=g.P0())
                .fill(tau)
                .label(element=self.uid + "_autorotation")
                .superimpose_rotation(
                    g.PZ(),
                    -np.sign(self.rturns) * (abs(self.rturns) - self.recovery_turns),
                    "world",
                )
            )
            rec2: State = (
                au2[-1]
                .copy(rvel=g.P0())
                .fill(trec)
                .superimpose_rotation(g.PY(), abs(self.pitch) * _inverted)
                .superimpose_angles(
                    g.PZ(-np.sign(self.rturns)) * rate * (trec.t - 0.5 * trec.t**2 / _trec),
                    "world",
                )
            )        
            return State.stack([nd, au, au2, rec2]).label(element=self.uid)
        else:
            au: State = (
                nd[-1]
                .copy(rvel=g.P0())
                .fill(tau)
                .label(element=self.uid + "_autorotation")
                .superimpose_rotation(
                    g.PZ(),
                    np.sign(self.turns) * (abs(self.turns) - self.drop_turns - self.recovery_turns),
                    "world",
                )
            )

            rec: State = (
                au[-1]
                .copy(rvel=g.P0())
                .fill(trec)
                .superimpose_rotation(g.PY(), abs(self.pitch) * _inverted)
                .superimpose_angles(
                    g.PZ(np.sign(self.turns)) * rate * (trec.t - 0.5 * trec.t**2 / _trec),
                    "world",
                )
            )             
            return State.stack([nd, au, rec]).label(element=self.uid)

    def describe(self):
        return f"Spin {self.turns}, {self.pitch}"

    def match_intention(self, transform: g.Transformation, flown: State) -> Spin:
        rot = flown.get_rotation()

        auto = State(
            flown.data.iloc[
                np.arange(
                    np.argmax(np.abs(flown.get_rotation()) > np.pi / 2),
                    np.where(abs(np.abs(rot[-1]) - np.abs(rot)) > np.pi / 2)[0][-1] + 1,
                )
            ]
        )

        pitch = np.mean(np.arctan2(auto.vel.z, auto.vel.x))

        return self.set_parms(
            height=flown.z[0] - flown.z[-1],
            turns=-np.sign(np.mean(auto.p)) * abs(self.turns),
            speed=np.mean(abs(flown.vel)),
            pitch=pitch,
        )
