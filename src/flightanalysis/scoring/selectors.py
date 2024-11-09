import numpy as np
import numpy.typing as npt
from flightdata import State
from flightanalysis.base.ref_funcs import RFuncBuilders

selectors = RFuncBuilders({})



@selectors.add
def last(fl: State, tp: State, vs: npt.NDArray):
    """return the last index"""
    return np.array([len(fl) - 1])


@selectors.add
def first(fl: State, tp: State, vs: npt.NDArray):
    """return the first index"""
    return np.array([0])

@selectors.add
def first_and_last(fl: State, tp: State, vs: npt.NDArray):
    """return the first index"""
    return np.array([0, len(fl)-1])


@selectors.add
def one(fl: State, tp: State, vs: npt.NDArray, i: int):
    """return the index i"""
    return np.array([i])


@selectors.add
def borders(fl: State, tp: State, vs: npt.NDArray, tb: float):
    """return the central portion of the array"""
    i0, i1 = fl.data.index.get_indexer([fl.data.index[0] + tb, fl.data.index[-1] - tb], 'nearest')
    if i0 < i1:
        return np.arange(i0, i1).astype(int)
    else:
        return np.array([]).astype(int)


@selectors.add
def after_slowdown(fl: State, tp: State, vs: npt.NDArray, sp: float):
    """return all the indices after the speed has dropped below min_speed"""
    id = np.argmax(abs(fl.vel.x) < sp) 
    if id == 0:
        id = len(fl)
    return np.arange(id, len(fl))


@selectors.add
def before_slowdown(fl: State, tp: State, vs: npt.NDArray, sp: float):
    """return all the indices before the speed has dropped below min_speed"""
    id = np.argmax(abs(fl.vel.x) < sp) 
    if id == 0:
        id = len(fl)
    return np.arange(id)


@selectors.add
def before_speedup(fl: State, tp: State, vs: npt.NDArray, sp: float):
    """return all the indices before the speed has accelerated above min_speed"""
    id = np.argmax(abs(fl.vel.x) > sp) 
    if id == 0:
        id = len(fl)
    return np.arange(id | len(fl))


@selectors.add
def after_speedup(fl: State, tp: State, vs: npt.NDArray, sp: float):
    """return all the indices after the speed has accelerated above min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) > sp), len(fl))


@selectors.add
def autorot_break(fl: State, tp: State, vs: npt.NDArray, rot: float):
    """return all the indices before the autorotation has turned by rotation"""
    # np.cumsum(g.Point.scalar_projection(fl.rvel, fl.vel) * fl.dt)
    return np.arange(np.argmax(np.abs(fl.get_rotation()) > rot)+1)


@selectors.add
def autorot_recovery(fl: State, tp: State, vs: npt.NDArray, rot: float):
    """return all the indices less than rotation from the end of the autorotation"""
    rots = fl.get_rotation()
    return np.arange(np.where((np.abs(rots[-1]) - np.abs(rots)) > rot)[0][-1], len(fl))

@selectors.add
def before_recovery(fl: State, tp: State, vs: npt.NDArray, rot: float):
    """return all the indices less than rotation from the end of the autorotation"""
    rots = fl.get_rotation()
    return np.arange(0, np.where((np.abs(rots[-1]) - np.abs(rots)) > rot)[0][-1] + 1)


@selectors.add
def autorotation(fl: State, tp: State, vs: npt.NDArray, brot: float, rrot: float):
    """return all the indeces during autorotation"""
    rot = fl.get_rotation()
    return np.arange(
        np.argmax(np.abs(fl.get_rotation()) > brot),
        np.where(abs(np.abs(rot[-1]) - np.abs(rot)) > rrot)[0][-1]+1,
    )

@selectors.add
def maximum(fl: State, tp: State, vs: npt.NDArray):
    """return the index with the highest value"""
    return np.array([np.argmax(vs)])

@selectors.add
def minimum(fl: State, tp: State, vs: npt.NDArray):
    """return the index with the lowest value"""
    return np.array([np.argmin(vs)])

@selectors.add
def absmax(fl: State, tp: State, vs: npt.NDArray):
    """return the index with the highest absolute value"""
    return np.array([np.argmax(np.abs(vs))])
