from .subsetters import Subsetters
from flightdata import State
import numpy as np
import geometry as g


def after_slowdown(fl: State, min_speed: float):
    """return all the indices after the speed has dropped below min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) < min_speed), len(fl))


def before_slowdown(fl: State, min_speed: float):
    """return all the indices before the speed has dropped below min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) < min_speed))


def before_speedup(fl: State, min_speed: float):
    """return all the indices before the speed has accelerated above min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) > min_speed))


def after_speedup(fl: State, min_speed: float):
    """return all the indices after the speed has accelerated above min_speed"""
    return np.arange(np.argmax(abs(fl.vel.x) > min_speed), len(fl))


def autorot_break(fl: State, rotation: float):
    """return all the indices before the autorotation has turned by rotation"""
    # np.cumsum(g.Point.scalar_projection(fl.rvel, fl.vel) * fl.dt)
    return np.arange(np.argmax(np.abs(fl.get_rotation()) > rotation))


def autorot_recovery(fl: State, rotation: float):
    """return all the indices less than rotation from the end of the autorotation"""
    rot = fl.get_rotation()
    return np.arange(
        np.where((np.abs(rot[-1]) - np.abs(rot)) > rotation)[0][-1], 
        len(fl)
    )


def autorotation(fl: State, break_rotation: float, recovery_rotation: float):
    """return all the indeces during autorotation"""
    rot = fl.get_rotation()
    return np.arange(
        np.argmax(np.abs(fl.get_rotation()) > break_rotation),
        np.where((np.abs(rot[-1]) - np.abs(rot)) > recovery_rotation)[0][-1]
    )


subs = Subsetters.from_funcs(
    after_slowdown,
    before_slowdown,
    before_speedup,
    after_speedup,
    autorot_break,
    autorot_recovery,
    autorotation
)
