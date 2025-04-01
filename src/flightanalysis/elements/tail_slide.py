from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from .element import Element
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class TailSlide(Element):
    """positive pitch rate for wheels down, negative for wheels up.
    All other signs do not matter. over_flop controls how fat past vertical down
    the nose drops.
    Speed should be negative.
    """

    parameters: ClassVar[list[str]] = Element.parameters + [
        "pitch_rate",
        "over_flop",
        "reset_rate",
        "height",
    ]
    pitch_rate: float
    over_flop: float
    reset_rate: float

    @property
    def height(self):
        return self.speed * ((np.pi + abs(self.over_flop)) / abs(self.pitch_rate) + abs(self.over_flop) / abs(self.reset_rate))

    def describe(self):
        return f"tailslide, pitch rate = {self.pitch_rate}"

    def create_template(self, istate: State, fl: State = None) -> State:
        _trot = (np.pi + abs(self.over_flop)) / abs(self.pitch_rate)
        _tcor = abs(self.over_flop) / abs(self.reset_rate)
        ttot = _trot + _tcor

        trot = g.Time.uniform(
            _trot, int(np.ceil(len(fl) * _trot / ttot)) if fl else None, 2
        )

        tcor = g.Time.uniform(
            _tcor, int(np.ceil(len(fl) * _tcor / ttot)) if fl else None, 2
        )

        rotation = (
            istate.copy(vel=g.PX(self.speed), rvel=g.P0())
            .fill(trot)
            .superimpose_rotation(
                g.PY(), (np.pi + abs(self.over_flop)) * np.sign(self.pitch_rate)
            )
        )

        correction = (
            rotation[-1]
            .copy(rvel=g.P0())
            .fill(tcor)
            .superimpose_rotation(
                g.PY(), -abs(self.over_flop) * np.sign(self.pitch_rate)
            )
        )

        return State.stack([rotation, correction])

    def match_axis_rate(self, pitch_rate: float) -> TailSlide:
        return self.set_parms(pitch_rate=pitch_rate)

    def match_intention(self, transform: g.Transformation, flown: State) -> TailSlide:
        direction = np.sign(np.sum(flown.q))
        total_rotation = np.abs(
            np.cumsum(abs(flown.rvel) * flown.dt * np.sign(flown.q))
        )
        over_flop = total_rotation.max() - np.pi
        iturn = np.argmax(total_rotation)
        _trot = flown.t[iturn] - flown.t[0]
        _tcor = flown.t[-1] - flown.t[iturn]

        return self.set_parms(
            speed=flown.wvel.z.mean(),
            pitch_rate=direction * (over_flop + np.pi) / _trot,
            over_flop=over_flop,
            reset_rate=over_flop / _tcor
        )

    def copy_direction(self, other: TailSlide) -> TailSlide:
        return self.set_parms(
            pitch_rate=abs(self.pitch_rate) * np.sign(other.pitch_rate)
        )
