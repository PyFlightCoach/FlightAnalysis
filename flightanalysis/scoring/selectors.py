import numpy as np
import numpy.typing as npt
from flightdata import State
from flightanalysis.base.ref_funcs import RFuncBuilders

selectors = RFuncBuilders({})


@selectors.add
def last(fl: State, vs: npt.NDArray):
    """return the last index"""
    return np.array([len(fl) - 1])


@selectors.add
def first(fl: State, vs: npt.NDArray):
    """return the first index"""
    return np.array([0])


@selectors.add
def one(fl: State, vs: npt.NDArray, i: int):
    """return the index i"""
    return np.array([i])


@selectors.add
def after_slowdown(fl: State, vs: npt.NDArray, sp: float):
    """return all the indices after the speed has dropped below min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) < sp), len(fl))


@selectors.add
def before_slowdown(fl: State, vs: npt.NDArray, sp: float):
    """return all the indices before the speed has dropped below min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) < sp))


@selectors.add
def before_speedup(fl: State, vs: npt.NDArray, sp: float):
    """return all the indices before the speed has accelerated above min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) > sp))


@selectors.add
def after_speedup(fl: State, vs: npt.NDArray, sp: float):
    """return all the indices after the speed has accelerated above min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) > sp), len(fl))


@selectors.add
def autorot_break(fl: State, vs: npt.NDArray, rot: float):
    """return all the indices before the autorotation has turned by rotation"""
    # np.cumsum(g.Point.scalar_projection(fl.rvel, fl.vel) * fl.dt)
    return np.arange(np.argmax(np.abs(fl.get_rotation()) > rot))


@selectors.add
def autorot_recovery(fl: State, vs: npt.NDArray, rot: float):
    """return all the indices less than rotation from the end of the autorotation"""
    rots = fl.get_rotation()
    return np.arange(np.where((np.abs(rots[-1]) - np.abs(rots)) > rot)[0][-1], len(fl))


@selectors.add
def autorotation(fl: State, vs: npt.NDArray, brot: float, rrot: float):
    """return all the indeces during autorotation"""
    rot = fl.get_rotation()
    return np.arange(
        np.argmax(np.abs(fl.get_rotation()) > brot),
        np.where((np.abs(rot[-1]) - np.abs(rot)) > rrot)[0][-1],
    )
