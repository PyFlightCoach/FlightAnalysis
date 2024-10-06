from flightdata import State
import geometry as g
import numpy as np

from .measurement import Measurement, measures as m
from enum import Enum


class Frame(Enum):
    WORLD = 0
    REF = 1


class Vec(Enum):
    VEL = 0
    ATT = 1


def angle_error_vis(fl: State, tp: State, vec: Vec):
    return Measurement._vector_vis(
        g.point.vector_rejection(
            fl.att.transform_point(fl.vel if Vec == Vec.VEL else g.PX()),
            tp.att.transform_point(tp.vel),
        ).unit(),
        fl.pos,
    )


def angle_error_parallel(fl: State, tp: State, proj: g.Point, frame: Frame, vec: Vec):
    """
    Angle errors parallel to the proj vector, which is a vector in either the
    world or the ref frame (tp[0].transform). Direction is the world frame scalar
    rejection of the velocity difference onto the template velocity vector.
    """
    # interesting vector in the world frame
    flvec = fl.att.transform_point(fl.vel if vec == Vec.VEL else g.PX())

    # proj vector in world frame
    proj = tp[0].att.transform_point(proj) if frame == Frame.REF else proj

    # error in the direction of the proj vector
    verr = g.point.vector_projection(flvec, proj)

    # sign of the error
    sign = np.where(g.Point.is_parallel(verr, proj), 1, -np.ones_like(verr.x))

    angles = sign * np.arctan(abs(verr) / abs(flvec))  # angle error

    return Measurement(angles, "rad", *angle_error_vis(fl, tp, vec))


def angle_error_about(fl: State, tp: State, proj: g.Point, frame: Frame, vec: Vec):
    """
    Angle errors about the proj vector, which is a vector in the ref_frame (tp[0].transform) or the world frame.
    Direction is the world frame scalar rejection of the velocity difference onto the template velocity vector.
    """

    # In the world frame create a loop coordinate frame.
    # z axis in the proj vector, x axis in the reference frame x axis
    rot = g.Quaternion.from_rotation_matrix(
        g.Coord.from_zx(
            g.P0(),
            proj if frame == Frame.WORLD else tp[0].att.transform_point(proj),
            tp[0].att.transform_point(g.PX()),
        ).rotation_matrix()
    )

    # get the velocities in the loop coordinate frame
    fl_lc_vel = rot.transform_point(
        fl.att.transform_point(fl.vel if vec == Vec.VEL else g.PX())
    )
    tp_lc_vel = rot.transform_point(tp.att.transform_point(tp.vel))

    angles = np.arctan2(fl_lc_vel.y, fl_lc_vel.x) - np.arctan2(tp_lc_vel.y, tp_lc_vel.x)

    return Measurement(np.unwrap(angles), "rad", *angle_error_vis(fl, tp, vec))


@m.add
def heading_track(fl: State, tp: State) -> Measurement:
    """angle error in the velocity vector about the world Z axis"""
    return angle_error_about(fl, tp, g.PZ(), Frame.WORLD, Vec.VEL)


@m.add
def heading_attitude(fl: State, tp: State) -> Measurement:
    """angle error in the body x axis about the world Z axis"""
    return angle_error_about(fl, tp, g.PZ(), Frame.WORLD, Vec.ATT)


@m.add
def climb_track(fl: State, tp: State) -> Measurement:
    """angle error in the velocity vector to the projection onto the world xy plane"""
    return angle_error_parallel(fl, tp, g.PZ(), Frame.WORLD, Vec.VEL)


@m.add
def rf_z_track(fl: State, tp: State) -> Measurement:
    """angle error in the velocity vector about the ref frame z axis"""
    return angle_error_about(fl, tp, g.PZ(), Frame.REF, Vec.VEL)


@m.add
def rf_y_track(fl: State, tp: State) -> Measurement:
    """angle error in the velocity vector about the ref frame y axis"""
    return angle_error_about(fl, tp, g.PY(), Frame.REF, Vec.VEL)


@m.add
def rf_z_attitude(fl: State, tp: State) -> Measurement:
    """angle error in the body x axis about the ref frame z axis"""
    return angle_error_about(fl, tp, g.PZ(), Frame.REF, Vec.ATT)


@m.add
def rf_y_attitude(fl: State, tp: State) -> Measurement:
    """angle error in the body x axis about the ref frame y axis"""
    return angle_error_about(fl, tp, g.PY(), Frame.REF, Vec.ATT)


@m.add
def loop_radial_track(fl: State, tp: State) -> Measurement:
    """angle error in the velocity vector about the loop radial direction"""
    return angle_error_about(
        fl, tp, Measurement.get_axial_direction(tp), Frame.REF, Vec.VEL
    )


@m.add
def loop_radial_attitude(fl: State, tp: State) -> Measurement:
    """angle error in the body x axis about the loop radial direction"""
    return angle_error_about(
        fl, tp, Measurement.get_axial_direction(tp), Frame.REF, Vec.ATT
    )


@m.add
def loop_axial_track(fl: State, tp: State) -> Measurement:
    """angle error in the velocity vector about the loop axial direction"""
    return angle_error_parallel(
        fl, tp, Measurement.get_axial_direction(tp), Frame.REF, Vec.VEL
    )


@m.add
def loop_axial_attitude(fl: State, tp: State) -> Measurement:
    """angle error in the body x axis about the loop axial direction"""
    return angle_error_parallel(
        fl, tp, Measurement.get_axial_direction(tp), Frame.REF, Vec.ATT
    )
