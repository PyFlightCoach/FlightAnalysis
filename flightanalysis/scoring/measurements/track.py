from flightdata import State
import geometry as g
import numpy as np

from .measurement import Measurement, measures as m



@m.add
def track_proj_vel(fl: State, tp: State, proj: g.Point = None):
    """
    We are only interested in velocity errors in the proj vector, which is a
    vector in the ref frame (tp[0].transform).
    Use this for things like loop axial track, with proj being the axial direction.
    Direction is the world frame scalar rejection of the velocity difference
    onto the template velocity vector.
    """
    proj = proj if proj else Measurement.get_proj(tp)

    verr = g.Point.vector_projection(
        tp[0].att.inverse().transform_point(fl.att.transform_point(fl.vel)),
        proj,
    )

    sign = np.where(g.Point.is_parallel(verr, proj), 1, -np.ones_like(verr.x))

    angles = sign * np.arctan(abs(verr) / abs(fl.vel))
    direction, vis = Measurement._vector_vis(verr.unit(), fl.pos)

    return Measurement(angles, "rad", direction, vis)

@m.add
def track_proj_ang(fl: State, tp: State, proj: g.Point = None):
    """
    We are only interested in errors about the proj vector, which is
    a vector in the ref_frame (tp[0].transform).
    Direction is the world frame scalar rejection of the velocity difference
    onto the template velocity vector.
    """
    proj = proj if proj else Measurement.get_proj(tp)

    rot = g.Quaternion.from_rotation_matrix(
        g.Coord.from_zx(
            g.P0(),
            tp[0].att.transform_point(proj),
            tp[0].att.transform_point(g.PX()),
        ).rotation_matrix()
    )

    fl_lc_vel = rot.transform_point(fl.att.transform_point(fl.vel))
    tp_lc_vel = rot.transform_point(tp.att.transform_point(tp.vel))

    angles = np.arctan2(fl_lc_vel.y, fl_lc_vel.x) - np.arctan2(
        tp_lc_vel.y, tp_lc_vel.x
    )

    direction, vis = Measurement._vector_vis(
        g.Point.vector_rejection(
            fl.att.transform_point(fl.vel), tp.att.transform_point(tp.vel)
        ).unit(),
        fl.pos,
    )

    return Measurement(np.unwrap(angles), "rad", direction, vis)

@m.add
def track_y(fl: State, tp: State) -> Measurement:
    """angle error in the velocity vector about the template Z axis"""
    return track_proj_ang(fl, tp, g.PZ())

@m.add
def track_z(fl: State, tp: State) -> Measurement:
    return track_proj_ang(fl, tp, g.PY())
