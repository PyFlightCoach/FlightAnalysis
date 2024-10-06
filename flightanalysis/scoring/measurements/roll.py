from flightdata import State
import geometry as g
import numpy as np

from .measurement import Measurement, measures as m


@m.add
def roll_angle(fl: State, tp: State) -> Measurement:
    """direction is the body X axis, value is equal to the roll angle difference from template"""
    body_roll_error = g.Quaternion.body_axis_rates(tp.att, fl.att) * g.PX()
    world_roll_error = fl.att.transform_point(body_roll_error)

    return Measurement(
        np.unwrap(abs(world_roll_error) * np.sign(body_roll_error.x)),
        "rad",
        *Measurement._roll_vis(fl, tp),
    )

@m.add
def roll_angle_proj(fl: State, tp: State, proj: g.Point) -> Measurement:
    """Direction is the body X axis, value is equal to the roll angle error.
    roll angle error is the angle between the body proj vector axis and the
    reference frame proj vector.
    proj normal of the plane to measure roll angles against.

    """
    wproj = tp[0].att.transform_point(proj)  # world proj vector
    fl_rf_proj = fl.att.inverse().transform_point(wproj)  # proj vector in body axis
    tp_rf_proj = tp.att.inverse().transform_point(
        wproj
    )  # proj vector in template body axis (body == track for template)

    angles = np.arctan2(fl_rf_proj.z, fl_rf_proj.y) - np.arctan2(
        tp_rf_proj.z, tp_rf_proj.y
    )
    angles[0] = angles[0] - 2 * np.pi * np.round(angles[0] / (2 * np.pi))

    return Measurement(
        np.unwrap(angles),
        "rad",
        *Measurement._roll_vis(fl, tp),
    )

@m.add
def roll_angle_p(fl: State, tp: State) -> Measurement:
    return roll_angle_proj(fl, tp, Measurement.get_axial_direction(tp))

@m.add
def roll_angle_y(fl: State, tp: State) -> Measurement:
    return roll_angle_proj(fl, tp, g.PY())

@m.add
def roll_angle_z(fl: State, tp: State) -> Measurement:
    return roll_angle_proj(fl, tp, g.PZ())



@m.add
def roll_rate(fl: State, tp: State) -> Measurement:
    """ratio error, direction is vector in the body X axis, length is equal to the roll rate"""
    wrvel = abs(fl.att.transform_point(fl.p * g.PX())) * np.sign(fl.p)
    return Measurement(
        Measurement.ratio(wrvel, np.mean(wrvel)),
        "ratio",
        *Measurement._roll_vis(fl, tp),
    )


@m.add
def abs_roll_rate(fl: State, tp: State) -> Measurement:
    
    wrvel = abs(fl.att.transform_point(fl.p * g.PX())) * np.sign(fl.p)
    rat = wrvel / np.mean(wrvel)
    return Measurement(
        rat,
        "ratio",
        *Measurement._roll_vis(fl, tp),
    )



@m.add
def autorotation_rate(fl: State, tp: State) -> Measurement:
    p = abs(fl.att.transform_point(fl.p * g.PX())) * np.sign(fl.p)

    return Measurement(
        Measurement.ratio(p, np.mean(tp.p)),
        "ratio",
        fl.pos,
        Measurement._pos_vis(fl.pos),
    )