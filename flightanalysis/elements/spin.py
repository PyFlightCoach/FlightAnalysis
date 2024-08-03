from __future__ import annotations
import numpy as np
import geometry as g
from flightdata import State
from .element import Element
from dataclasses import dataclass
from typing import ClassVar
from .loop import Loop


@dataclass
class Spin(Element):
    parameters: ClassVar[list[str]] = Element.parameters + \
        ['height', 'turns', 'pitch', 'drop_turns', 'recovery_turns', 'rate']

    height: float
    turns: float
    pitch: float
    drop_turns: float
    recovery_turns: float

    @property
    def rate(self):
        return self.speed * (abs(self.turns) + self.drop_turns * (2/np.pi - 1) + self.recovery_turns) / self.height
        #return (self.turns + self.drop_turns + self.recovery_turns) * self.speed / self.height
    
    @staticmethod
    def get_height(speed: float, rate: float, turns: float, drop_turns: float, recovery_turns: float):
        return (abs(turns) + drop_turns * (2/np.pi - 1) + recovery_turns) * speed / rate

    def create_template(self, istate: State, time: g.Time=None) -> State:
        _inverted = 1 if istate.transform.rotation.is_inverted()[0] else -1
        rate= self.rate

        _ttot = (abs(self.turns) + self.drop_turns + self.recovery_turns) / rate
        _tdr = 2 * self.drop_turns / rate
        _trec = 2 * self.recovery_turns / rate
        
        time = Element.create_time(_ttot, time)

        ind = int(np.ceil(len(time) * _tdr / _ttot))
        irec = int(np.ceil(len(time) * _trec / _ttot))

        
        tnd = time[0:ind+1]
        nd: State = Loop(self.uid + "_nose_drop", self.speed, 0.5*np.pi*_inverted, 
                  2*self.drop_turns * self.speed / (rate * np.pi), 0, 0
        ).create_template(
            istate, tnd
        ).superimpose_rotation(
            g.PY(), -abs(self.pitch) * _inverted
        ).superimpose_angles(
            g.PZ(np.sign(self.turns) * self.drop_turns) * tnd.t / tnd.t[-1],
            "world"
        )

        tau = time[ind:-irec+1].reset_zero()
        au: State = nd[-1].copy(rvel=g.P0()).fill(
            tau
        ).label(element=self.uid + '_autorotation').superimpose_rotation(
            g.PZ(),
            np.sign(self.turns) * (abs(self.turns) - self.drop_turns - self.recovery_turns),
            'world'
        )

        trec = time[-irec-1:-1].reset_zero()
        rec: State = au[-1].copy(rvel=g.P0()).fill(
            trec
        ).superimpose_rotation(
            g.PY(), 
            abs(self.pitch) * _inverted
        ).superimpose_angles(
            g.PZ(np.sign(self.turns) * self.recovery_turns) * trec.t / trec.t[-1],
            "world"
        ).label(element=self.uid + '_recovery')

        return State.stack([nd, au, rec])

    def describe(self):
        return f"Spin {self.turns}, {self.pitch}"
    
    def match_intention(self, transform: g.Transformation, flown: State) -> Spin:
        time = Element.create_time(self.length / self.speed, flown)
        ipb = int(np.ceil(len(time) * abs(self.break_roll / self.roll)))
        irec = int(np.ceil(len(time) * abs(self.recovery_roll / self.roll)))


        pitch = np.arctan2(flown.vel.z, flown.vel.x)[ipb:-irec]
        maxpitch = np.max(pitch)
        minpitch = np.min(pitch)
        pitch = maxpitch if abs(maxpitch) > abs(minpitch) else minpitch
        return self.set_parms(
            length=abs(self.length_vec(transform, flown))[0],
            roll=np.sign(np.mean(flown.p)) * abs(self.roll),
            speed=np.mean(abs(flown.vel)),
            pitch=pitch
        )
    