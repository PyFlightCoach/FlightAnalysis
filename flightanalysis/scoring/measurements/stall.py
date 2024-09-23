from flightdata import State
import geometry as g
import numpy as np

from .measurement import Measurement, measures as m



@m.add
def length(fl: State, tp: State, direction: g.Point = None) -> Measurement:
    """Distance from the ref frame origin in the prescribed direction"""
    ref_frame = tp[0].transform
    distance = ref_frame.q.inverse().transform_point(
        fl.pos - ref_frame.pos
    )  # distance in the ref_frame

    v = (
        distance
        if direction is None
        else g.Point.vector_projection(distance, direction)
    )

    return Measurement(
        g.Point.scalar_projection(v, direction),
        "m",
        *Measurement._vector_vis(ref_frame.q.transform_point(distance), fl.pos),
    )

@m.add
def stallturn_width(fl: State, tp: State) -> Measurement:
    return length(fl, tp, g.PY())




@m.add
def alpha(fl: State, tp: State) -> Measurement:
    """Estimate alpha based on Z force"""
    alpha_acc = -4.6 * fl.acc.z / (abs(fl.vel) ** 2)  # 2.6
    return Measurement(alpha_acc, "rad", *Measurement._pitch_vis(fl, tp))

@m.add
def spin_alpha(fl: State, tp: State) -> Measurement:
    """Estimate alpha based on Z force, positive for correct direction (away from ground)"""
    # 2.6
    return Measurement(
        4.6
        * fl.acc.z
        / (abs(fl.vel) ** 2)
        * (fl[0].inverted().astype(int) * 2 - 1),
        "rad",
        *Measurement._pitch_vis(fl, tp),
    )

@m.add
def delta_alpha(fl: State, tp: State) -> Measurement:
    return Measurement(
        np.gradient(-4.6 * fl.acc.z / (abs(fl.vel) ** 2)) / fl.dt,
        "rad/s",
        *Measurement._pitch_vis(fl, tp),
    )

@m.add
def pitch_rate(fl: State, tp: State) -> Measurement:
    return Measurement(fl.q, "rad/s", *Measurement._pitch_vis(fl, tp))

@m.add
def pitch_down_rate(fl: State, tp: State) -> Measurement:
    return Measurement(
        fl.q * (fl.inverted().astype(int) * 2 - 1),
        "rad/s",
        *Measurement._pitch_vis(fl, tp),
    )

@m.add
def delta_p(fl: State, tp: State) -> Measurement:
    roll_direction = np.sign(fl.p.mean())
    return Measurement(
        roll_direction * np.gradient(fl.p) / fl.dt,
        "rad/s/s",
        *Measurement._pitch_vis(fl, tp),
    )
