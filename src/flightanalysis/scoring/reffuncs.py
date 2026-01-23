from flightanalysis.base.ref_funcs import RFuncBuilders
from flightdata import State


measures = RFuncBuilders({})
smoothers = RFuncBuilders({})
selectors = RFuncBuilders({})
visor = RFuncBuilders({})

rfuncs = dict(
    measures=measures,
    smoothers=smoothers,
    selectors=selectors,
    visor=visor,
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

