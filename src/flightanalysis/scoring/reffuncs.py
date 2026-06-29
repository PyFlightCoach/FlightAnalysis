from __future__ import annotations
from flightanalysis.scoring.measurement import (
    Measure,
    Measurement,
    MeasureFunc,
    VisorFunc,
)
from flightanalysis.scoring.selector import Selector, SelectorFunc
from flightanalysis.base.ref_funcs import RFuncBuilders, RefFunc
from flightdata import State
import pandas as pd

measures = RFuncBuilders({})
selectors = RFuncBuilders({})
visors = RFuncBuilders({})
inter_visors = RFuncBuilders({})
box_measures = RFuncBuilders({})
box_visors = RFuncBuilders({})


def measure(
    description: str,
    visor: VisorFunc | list[VisorFunc] = [],
    unit: str = "",
) -> RefFunc:

    def inner(func: MeasureFunc) -> Measurement:
        return measures.add(description)(
            Measure(
                func.__name__,
                func,
                [visor] if not pd.api.types.is_list_like(visor) else visor,
                unit,
            )
        )

    return inner

def selector(
    description: str,
    left: bool = True, 
    right: bool = True
) -> RefFunc:

    def inner(func: SelectorFunc) -> Selector:
        return selectors.add(description)(Selector(func.__name__, func, left, right))

    return inner


rfuncs = dict(
    measures=measures,
    selectors=selectors,
    visors=visors,
    inter_visors=inter_visors,
    box_measures=box_measures,
    box_visors=box_visors,
)


@selector("The last data point", left=False)
def last(fl: State):
    """return the last index"""
    return [-1]


@selector("The first data point", right=False)
def first(fl: State):
    """return the first index"""
    return [0]


@selector("A single specified index", left=False, right=False)
def one(fl: State, i: int):
    """return the index i"""
    return [i]
