from flightanalysis.base.ref_funcs import RFuncBuilders
from flightdata import State
import numpy as np
import numpy.typing as npt

measures = RFuncBuilders({})
smoothers = RFuncBuilders({})
selectors = RFuncBuilders({})
visor = RFuncBuilders({})


@smoothers.add
def final(data, dt, *args, **kwargs):
    """This is meant to be applied as the final filter in all downgrades.
    It corrects the first and last value based on the time step.
    """    
    if len(data) > 2:
        pass
        #data[0] = (data[0] - data[1]) * dt[0] / dt[1] + data[1]
        #data[-1] = (data[-1] - data[-2]) * dt[-2] / dt[-3] + data[-2]
    return data


@selectors.add
def last(fl: State):
    """return the last index"""
    return [-1]


@selectors.add
def first(fl: State):
    """return the first index"""
    return [0]


@selectors.add
def one(fl: State, i: int):
    """return the index i"""
    return [i]

