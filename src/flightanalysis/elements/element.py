from __future__ import annotations
import numpy as np
import pandas as pd
from flightdata import State, Collection
from flightanalysis.scoring import Measurement
import geometry as g
from json import load
import inspect
from typing import Self, ClassVar
from dataclasses import dataclass


class ElementError(Exception):
    pass


@dataclass
class Element:   
    parameters: ClassVar[list[str]] = ["speed"]
    uid: str
    speed: float

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
        return np.all([abs(getattr(self, p) - getattr(other, p)) < 0.01 for p in self.__class__.parameters])

    def __repr__(self):
        args = ['uid'] + inspect.getfullargspec(self.__init__).args[1:-1]
        return f'{self.__class__.__name__}({", ".join([str(getattr(self,a)) for a in args])})'

    def to_dict(self):
        return dict(
            kind=self.__class__.__name__, 
            uid=self.uid,
            **{p: getattr(self, p) for p in self.parameters}
        )

    def set_parms(self, **parms):
        kwargs = {k:v for k, v in self.__dict__.items() if not k[0] == "_"}

        for key, value in parms.items():
            if key in kwargs:
                kwargs[key] = value
        
        return self.__class__(**kwargs)

    def ref_frame(self, template: State) -> g.Transformation:
        return template[0].transform

    @staticmethod
    def create_time(duration: float, fl: State=None):
        
        if not fl:
            n = max(int(np.ceil(duration * State._construct_freq)), 3)
            return g.Time.from_t(
                np.linspace(0, duration, n)
            )
        else:
            return fl.time.reset_zero().scale(duration)

    @classmethod
    def from_name(Cls, name) -> Element:
        return {C.__name__.lower(): C for C in Cls.__subclasses__()}[name.lower()]

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
    

    #
    def length_vec(self, itrans, fl):
        return fl.pos[-1] - fl.pos[0]
    
    def create_template(self, istate: State, time: g.Time=None) -> State:
        raise Exception('Not available on base class')

    def match_intention(self, itrans: g.Transformation, flown: State) -> Self:
        raise Exception('Not available on base class')


class Elements(Collection):
    VType=Element
    def get_parameter_from_element(self, element_name: str, parameter_name: str):
        return getattr(self.data[element_name], parameter_name)  
    
    @staticmethod
    def from_dicts(data) -> Self:
        return Elements([Element.from_dict(d) for d in data])
            
    def copy_directions(self, other: Self) -> Self:
        return Elements([es.copy_direction(eo) for es, eo in zip(self, other)])
    
    def to_df(self):
        params = pd.DataFrame(
            [{k: getattr(e, k) for k in inspect.getfullargspec(e.__init__).args[1:-1]} for e in self]
        )
        names = pd.DataFrame(
            [[e.uid, e.__class__.__name__] for e in self], columns=['name', 'class']
        )
        return pd.concat([names, params], axis=1).fillna('-')
