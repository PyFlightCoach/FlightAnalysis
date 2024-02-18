import enum
from typing import List, Callable, Union, Dict, Tuple
import numpy as np
from flightanalysis.elements import *
from inspect import getfullargspec
from functools import partial
from . import ManParm, ManParms, Opp, ItemOpp
from flightdata import Collection
from numbers import Number
from . import Collector, Collectors
import inspect
from uuid import uuid1


class ElDef:
    """This class creates a function to build an element (Loop, Line, Snap, Spin, Stallturn)
    based on a ManParms collection. 

    The eldef also contains a set of collectors. These are a dict of str:callable pairs
    that collect the relevant parameter for this element from an Elements collection.
    """
    def __init__(self, name, Kind, props: Dict[str, Union[Number, Opp]]):
        """ElDef Constructor

        Args:
            name (_type_): the name of the Eldef, must be unique and work as an attribute
            Kind (_type_): the class of the element (Loop, Line etc)
            props (dict): The element property generators (Number, Opp)
        """
        self.name = name
        self.Kind = Kind
        self.props = props       
        self.collectors = Collectors.from_eldef(self)

    def get_collector(self, name) -> Collector:
        return self.collectors[f"{self.name}.{name}"]

    def to_dict(self):
        return dict(
            name = self.name,
            Kind = self.Kind.__name__,
            props = {k: str(v) for k, v in self.props.items()}
        )

    def __repr__(self):
        return f"ElDef({self.name}, {self.Kind.__name__}, {self.props})"

    @staticmethod
    def from_dict(data: dict, mps: ManParms): 
        return ElDef(
            name=data["name"],
            Kind = Element.from_name(data["Kind"]),
            props = {k: ManParm.parse(v, mps) for k, v in data["props"].items()}
        )


    def __call__(self, mps: ManParms, **kwargs) -> Element:
        el_kwargs = {}
        args = getfullargspec(self.Kind.__init__).args
        for pname, prop in self.props.items():
            if pname in args:
                
                if isinstance(prop, ManParm):
                    if prop.kind=='Combination':

                        el_kwargs[pname] = mps.data[prop.name].value[id]

                    else:
                        el_kwargs[pname] = mps.data[prop.name].value 
                elif isinstance(prop, Opp):
                    el_kwargs[pname] = prop(mps)
                elif isinstance(prop, Number):
                    el_kwargs[pname] = prop
                else:
                    raise TypeError(f"Invalid prop type {prop.__class__.__name__}")
            
        try:
            return self.Kind(uid=self.name, **el_kwargs) 
        except Exception as e:
            raise Exception(f"Error creating {self.name}, a {self.Kind.__name__} with {el_kwargs}") from e
    
    def build(Kind, name, *args, **kwargs):
        elargs = list(inspect.signature(Kind.__init__).parameters)[1:-1]
        for arg, argname in zip(args, elargs[:len(args)] ):
            kwargs[argname] = arg
        
        ed = ElDef(name, Kind, kwargs)
        
        for key, value in kwargs.items():
            if isinstance(value, ManParm):
                value.append(ed.get_collector(key))
            elif isinstance(value, ItemOpp):
                value.a.assign(value.item, ed.get_collector(key))
        
        return ed

    def rename(self, new_name):
        return ElDef(new_name, self.Kind, self.pfuncs)
    
    @property
    def id(self):
        return int(self.name.split("_")[1])





class ElDefs(Collection):
    VType=ElDef
    uid="name"
    """This class wraps a dict of ElDefs, which would generally be used sequentially to build a manoeuvre.
    It provides attribute access to the ElDefs based on their names. 
    """

    @staticmethod
    def from_dict(data: dict, mps: ManParms):
        return ElDefs([ElDef.from_dict(v, mps) for v in data.values()])

    def to_dict(self):
        return {v.name: v.to_dict() for v in self}
    
    def get_new_name(self): 
        new_id = 0 if len(self.data) == 0 else list(self.data.values())[-1].id + 1
        return f"e_{new_id}"

    def add(self, ed: Union[ElDef, List[ElDef]]) -> Union[ElDef, List[ElDef]]:
        """Add a new element definition to the collection. Returns the ElDef

        Args:
            ed (Union[ElDef, List[ElDef]]): The ElDef or list of ElDefs to add

        Returns:
            Union[ElDef, List[ElDef]]: The ElDef or list of ElDefs added
        """
        if isinstance(ed, ElDef):
            self.data[ed.name] = ed
            return ed
        else:
            return [self.add(e) for e in ed]


    def builder_list(self, name:str) ->List[Callable]:
        """A list of the functions that return the requested parameter when constructing the elements from the mps"""
        return [e.props[name] for e in self if name in e.props]

    def builder_sum(self, name:str, oppname=None) -> Callable:
        """A function to return the sum of the requested parameter used when constructing the elements from the mps"""
        opp = sum(self.builder_list(name))
        if hasattr(opp, name):
            opp.name = uuid1() if oppname is None else oppname
        return opp

    def collector_list(self, name: str) -> Collectors:
        """A list of the functions that return the requested parameter from an elements collection"""
        return Collectors([e.get_collector(name) for e in self if f"{e.name}.{name}" in e.collectors.data])


    def collector_sum(self, name, oppname=None) -> Callable:
        """A function that returns the sum of the requested parameter from an elements collection"""
        opp = sum(self.collector_list(name))
        if hasattr(opp, name):
            opp.name = uuid1() if oppname is None else oppname
        return opp
    

    def get_centre(self, mps: ManParms) -> Tuple[int, float]:
        """Get the centre element id and the location of the centre within it.

        Returns:
            Tuple[int, float]: elementid, position within element
        """
        lengths = [el(mps).length for el in self]
        cumlength = np.cumsum(lengths)
        mid_point = cumlength[-1] / 2

        for i, clen in enumerate(cumlength):
            if clen > mid_point:

                return i,  (mid_point - cumlength[i-1]) / lengths[i]
        else:
            raise Exception('should not happen')
