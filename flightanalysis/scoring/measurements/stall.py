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


def estimate_alpha(mode: str, accz: float, vel: float) -> float:
    factor = dict(f3a=4.6, iac=112)
    return -factor[mode] * accz / (abs(vel) ** 2)


def alpha(fl: State, tp: State, mode: str) -> Measurement:
    """Estimate alpha based on Z force"""
    return Measurement(
        estimate_alpha(mode, fl.acc.z, fl.vel), "rad", *Measurement._pitch_vis(fl, tp)
    )

@m.add
def alpha_f3a(fl: State, tp: State) -> Measurement:
    return alpha(fl, tp, "f3a")

@m.add
def alpha_iac(fl: State, tp: State) -> Measurement:
    return alpha(fl, tp, "iac")


def spin_alpha(fl: State, tp: State, mode:str) -> Measurement:
    """Estimate alpha based on Z force, positive for correct direction (away from ground)"""
    # 2.6
    return Measurement(
        -estimate_alpha(mode, fl.acc.z, fl.vel) * (fl[0].inverted().astype(int) * 2 - 1),
        "rad",
        *Measurement._pitch_vis(fl, tp),
    )
@m.add
def spin_alpha_f3a(fl: State, tp: State) -> Measurement:
    return spin_alpha(fl, tp, "f3a")

@m.add
def spin_alpha_iac(fl: State, tp: State) -> Measurement:
    return spin_alpha(fl, tp, "iac")


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
