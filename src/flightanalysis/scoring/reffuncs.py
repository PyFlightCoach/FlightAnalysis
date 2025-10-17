from flightanalysis.base.ref_funcs import RFuncBuilders
from flightdata import State


measures = RFuncBuilders({})
smoothers = RFuncBuilders({})
selectors = RFuncBuilders({})
visor = RFuncBuilders({})


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

