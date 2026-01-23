from flightanalysis.base.ref_funcs import RFuncBuilders
from flightdata import State


measures = RFuncBuilders({})
selectors = RFuncBuilders({})
visors = RFuncBuilders({})

rfuncs = dict(
    measures=measures,
    selectors=selectors,
    visors=visors,
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

