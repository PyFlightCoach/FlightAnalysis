from __future__ import annotations
from typing import Callable
import numpy.typing as npt
from flightanalysis.elements import Elements
from flightanalysis.scoring.measurement import Measure, Measurement
from flightanalysis.base.ref_funcs import RFuncBuilders, RefFunc
from flightdata import State


measures = RFuncBuilders({})
smoothers = RFuncBuilders({})
selectors = RFuncBuilders({})
<<<<<<< HEAD
visor = RFuncBuilders({})
=======
visors = RFuncBuilders({})
inter_visors = RFuncBuilders({})
box_measures = RFuncBuilders({})
box_visors = RFuncBuilders({})

def measure(
    description: str,
    visor: Callable[[State, State, Measurement], npt.NDArray],
    unit: str = "",
) -> RefFunc:
    def inner(func: Callable[[Elements, State, State], npt.NDArray]) -> Measurement:
        return measures.add(description)(Measure(func.__name__, func, visor, unit))

    return inner

>>>>>>> newmeasure

rfuncs = dict(
    measures=measures,
    smoothers=smoothers,
    selectors=selectors,
<<<<<<< HEAD
    visor=visor,
=======
    visors=visors,
    inter_visors=inter_visors,
    box_measures=box_measures,
    box_visors=box_visors,
>>>>>>> newmeasure
)


@selectors.add("The last data point")
def last(fl: State):
    """return the last index"""
    return [-1]


@selectors.add("The first data point")
def first(fl: State):
    """return the first index"""
    return [0]


@selectors.add("A single specified index")
def one(fl: State, i: int):
    """return the index i"""
    return [i]
