from __future__ import annotations
from flightanalysis.scoring.measurement import (
    Measure,
    Measurement,
    MeasureFunc,
    VisorFunc,
)
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


rfuncs = dict(
    measures=measures,
    selectors=selectors,
    visors=visors,
    inter_visors=inter_visors,
    box_measures=box_measures,
    box_visors=box_visors,
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
