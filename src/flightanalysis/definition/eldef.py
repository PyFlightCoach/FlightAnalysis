from dataclasses import dataclass
from inspect import getfullargspec
from numbers import Number
from typing import Callable, List, Tuple, Union
from uuid import uuid1

import numpy as np
from flightdata import Collection

from flightanalysis.elements import Element
from flightanalysis.scoring.downgrade import DownGrades

from . import Collector, Collectors, ItemOpp, ManParm, ManParms, Opp, SumOpp


@dataclass
class ElDef:
    """This class creates a function to build an element (Loop, Line, Snap, Spin, Stallturn)
    based on a ManParms collection.

    The eldef also contains a set of collectors. These are a dict of str:callable pairs
    that collect the relevant parameter for this element from an Elements collection.
    """

    name: str  # the name of the Eldef, must be unique and work as an attribute
    Kind: object  # the class of the element (Loop, Line etc)
    props: dict[str, Number | Opp]  # The element property generators (Number, Opp)
    dgs: DownGrades  # The DownGrades applicable this element

    def get_collector(self, name) -> Collector:
        return Collector(self.name, name)

    def to_dict(self, longdgs=True):
        return dict(
            name=self.name,
            Kind=self.Kind.__name__,
            props={k: str(v) for k, v in self.props.items()},
            dgs=self.dgs.to_dict() if longdgs else self.dgs.to_list(),
        )

    def __repr__(self):
        return f"ElDef({self.name}, {self.Kind.__name__}, {[f'{k[0]}={str(v)}' for k, v in self.props.items()]}, {[dg.name for dg in self.dgs]})"

    @staticmethod
    def from_dict(data: dict, mps: ManParms):
        return ElDef(
            name=data["name"],
            Kind=Element.from_name(data["Kind"]),
            props={k: ManParm.parse(v, mps) for k, v in data["props"].items()},
            dgs=DownGrades.from_dict(data["dgs"]),
        )

    def __call__(self, mps: ManParms) -> Element:
        el_kwargs = {}
        args = getfullargspec(self.Kind.__init__).args
        for pname, prop in self.props.items():
            if pname in args:
                if isinstance(prop, ManParm):
                    if prop.kind == "Combination":
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
            raise Exception(
                f"Error creating {self.name}, a {self.Kind.__name__} with {el_kwargs}"
            ) from e

    @staticmethod
    def build(Kind, name: str, props: list[Opp | Number]):
        pnames = getfullargspec(Kind.__init__).args[2:]
        ed = ElDef(name, Kind, {k: v for k, v in zip(pnames, props)}, DownGrades([]))

        for key, value in zip(pnames, props):
            if isinstance(value, ManParm):
                value.append(ed.get_collector(key))
            elif isinstance(value, ItemOpp):
                value.a.assign(value.item, ed.get_collector(key))

        return ed

    def rename(self, new_name):
        return ElDef(new_name, self.Kind, self.pfuncs)

    @property
    def id(self):
        try:
            return int(self.name.split("_")[1])
        except Exception:
            return -1


class ElDefs(Collection):
    """This class wraps a dict of ElDefs, which would generally be used sequentially to build a manoeuvre.
    It provides attribute access to the ElDefs based on their names.
    """

    VType = ElDef
    uid = "name"

    @staticmethod
    def from_dict(data: dict, mps: ManParms):
        return ElDefs([ElDef.from_dict(v, mps) for v in data.values()])

    def to_dict(self, dgs=True):
        return {v.name: v.to_dict(dgs) for v in self}

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

    def builder_list(self, name: str) -> List[Callable]:
        """A list of the functions that return the requested parameter when constructing the elements from the mps"""
        return [e.props[name] for e in self if name in e.props]

    def builder_sum(self, name: str, oppname=None) -> Callable:
        """A function to return the sum of the requested parameter used when constructing the elements from the mps"""
        blist = self.builder_list(name)
        opp = blist[0] if len(blist) == 1 else SumOpp(name, blist)
        if hasattr(opp, name):
            opp.name = uuid1() if oppname is None else oppname
        return opp

    def collector_list(self, name: str) -> Collectors:
        """A list of the functions that return the requested parameter from an elements collection"""
        return Collectors(
            [e.get_collector(name) for e in self if name in e.Kind.parameters]
        )

    def collector_sum(self, name, oppname=None) -> Callable:
        """A function that returns the sum of the requested parameter from an elements collection"""
        clist = self.collector_list(name)
        opp = clist[0] if len(clist) == 1 else SumOpp(name, clist)
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
                return i, (mid_point - cumlength[i - 1]) / lengths[i]
        else:
            raise Exception("should not happen")
