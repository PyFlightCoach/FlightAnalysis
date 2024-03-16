from __future__ import annotations
import numpy as np
import pandas as pd
from flightdata import State, Collection
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.scoring import Measurement, DownGrade, DownGrades, Results
import geometry as g
from json import load
import inspect
from typing import Self, Tuple


class ElementError(Exception):
    pass


class Element:   
    parameters = ["speed"]

    def __init__(self, uid: str, speed: float):        
        self.uid = uid
        if speed < 0:
            raise ValueError("negative speeds are not allowed")
        self.speed = speed

    def get_data(self, st: State):
        return st.get_element(self.uid)

    def _add_rolls(self, el: State, roll: float) -> State:
        if not roll == 0:
            el = el.superimpose_rotation(g.PX(), roll)
        return el.label(element=self.uid)

    def __eq__(self, other):
        if not self.__class__ == other.__class__:
            return False
        if not self.uid == other.uid:
            return False
        return np.all([np.isclose(getattr(self, p), getattr(other, p), 0.01) for p in self.__class__.parameters])

    def __repr__(self):
        args = ['uid'] + inspect.getfullargspec(self.__init__).args[1:-1]
        return f'{self.__class__.__name__}({", ".join([str(getattr(self,a)) for a in args])})'

    def to_dict(self, exit_only: bool=False):
        return dict(
            kind=self.__class__.__name__, 
            **{p: getattr(self, p) for p in self.parameters},
            uid=self.uid,
            scoring = self.exit_scoring.to_dict() if exit_only else self.intra_scoring.to_dict() 
        )

    def set_parms(self, **parms):
        kwargs = {k:v for k, v in self.__dict__.items() if not k[0] == "_"}

        for key, value in parms.items():
            if key in kwargs:
                kwargs[key] = value
        
        return self.__class__(**kwargs)

    def score_series_builder(self, index):
        return lambda data: pd.Series(data, index=index)

    def analyse(self, flown:State, template:State) -> Results:
        return self.intra_scoring.apply(self, flown, template)

    def analyse_exit(self, fl, tp) -> Results:
        return self.exit_scoring.apply(self, fl, tp)

    def ref_frame(self, template: State) -> g.Transformation:
        return template[0].transform

    @staticmethod
    def create_time(duration: float, time: g.Time=None):
        if time is None:
            n = max(int(np.ceil(duration * State._construct_freq)), 3)
            return g.Time.from_t(
                np.linspace(0, duration, n)
            )
        else:
            return time.reset_zero().scale(duration)

    @property
    def intra_scoring(self) -> DownGrades:
        return DownGrades()

    @property
    def exit_scoring(self):
        return DownGrades([
            DownGrade(Measurement.track_y, F3A.single.track),
            DownGrade(Measurement.track_z, F3A.single.track),
            DownGrade(Measurement.roll_angle, F3A.single.roll),
        ])

    @classmethod
    def from_name(Cls, name) -> Element:
        for Child in Cls.__subclasses__():
            if Child.__name__.lower() == name.lower():
                return Child

    @classmethod
    def from_dict(Cls, data: dict):
        El = Element.from_name(data["kind"].lower())
        
        _args = inspect.getfullargspec(El.__init__)[0]

        return El(
            **{k: v for k, v in data.items() if k in _args}
        )
    
    @classmethod
    def from_json(Cls, file):
        with open(file, "r") as f:
            return Element.from_dict(load(f))

    def copy(self):
        return self.__class__(
            **{p: getattr(self, p) for p in inspect.getfullargspec(self.__init__).args[1:]}
        )
    
    def length_visibility(self, st: State):
        pos = st.pos
        return Measurement._vector_vis(pos[-1] - pos[0], pos.mean())
    
    def rate_visibility(self, st: State):
        return Measurement._vector_vis(st.vel.mean(), st.pos.mean())

    def length_vec(self, itrans, fl):
        return fl.pos[-1] - fl.pos[0]

    
    def create_template(self, istate: State, time: g.Time=None) -> State:
        raise Exception('Not available on base class')

    def match_intention(self, itrans: g.Transformation, flown: State) -> Self:
        raise Exception('Not available on base class')

    def score(self, istate: State, fl: State) -> Tuple[Results, State]:
        tp = self.create_template(istate, fl.time)
        if self.uid=='entry_line':
            res = self.analyse_exit(fl, tp)
        else:
            res = self.analyse(fl, tp)
        return res, tp
        
    @staticmethod
    def optimise_split(istate: State, el1: Element, el2: Element, fl1: State, fl2: State):
        
        def get_score(cel1: Element, cel2: Element, cfl1: State, cfl2: State):
            res, tp = cel1.match_intention(istate.transform, cfl1).score(istate, cfl1)
            ist2=State.from_transform(g.Transformation(tp.att[-1], cfl2.pos[0]), vel=tp.vel[-1])
            res2, tp2 = cel2.match_intention(ist2.transform, cfl2).score(ist2, cfl2)
            return res.total + res2.total
        
        dgs = {0: get_score(el1, el2, fl1, fl2)}
        
        steps=int(len(fl2) > len(fl1)) * 2 - 1
        
        new_dg = get_score(el1, el2, *State.shift_multi(steps, fl1, fl2))
        if new_dg > dgs[0]:
            steps=-steps
        else:
            steps+=np.sign(steps)
            dgs[steps] = new_dg
            
        while True:
            if (steps>0 and len(fl2)<=steps+3) or (steps<0 and len(fl1) <=-steps+3):
                break
            new_dg = get_score(el1, el2, *State.shift_multi(steps, fl1, fl2))
            if new_dg < list(dgs.values())[-1]:
                steps+=np.sign(steps)
                dgs[steps] = new_dg
            else:
                break
        min_dg_step = np.argmin(np.array(list(dgs.values())))
        out_steps = list(dgs.keys())[min_dg_step]
        
        return out_steps


class Elements(Collection):
    VType=Element
    def get_parameter_from_element(self, element_name: str, parameter_name: str):
        return getattr(self.data[element_name], parameter_name)  
    
    @staticmethod
    def from_dicts(data) -> Self:
        return Elements([Element.from_dict(d) for d in data])
            
    def copy_directions(self, other: Self) -> Self:
        return Elements([es.copy_direction(eo) for es, eo in zip(self, other)])
    
