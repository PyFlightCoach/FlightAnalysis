from __future__ import annotations
from flightdata import State
import geometry as g
import numpy as np
import pandas as pd
import numpy.typing as npt
from dataclasses import dataclass
from typing import Union, Self


@dataclass()
class Measurement:
    value: npt.NDArray
    unit: str
    direction: g.Point
    visibility: npt.NDArray
    keys: npt.NDArray = None

    def __len__(self):
        return len(self.value)

    def __getitem__(self, sli):
        return Measurement(
            self.value[sli],
            self.unit,
            self.direction[sli],
            self.visibility[sli],
        )

    def to_dict(self):
        return dict(
            value=list(self.value),
            unit=self.unit,
            direction=self.direction.to_dicts(),
            visibility=list(self.visibility),
            keys=list(self.keys) if self.keys is not None else None,
        )

    def __repr__(self):
        if len(self.value) == 1:
            return f"Measurement({self.value}, {self.direction}, {self.visibility})"
        else:
            return f"Measurement(\nvalue:\n={pd.DataFrame(self.value).describe()}\nvisibility:\n{pd.DataFrame(self.visibility).describe()}\n)"

    @staticmethod
    def from_dict(data) -> Measurement:
        return Measurement(
            np.array(data["value"]),
            data["unit"],
            g.Point.from_dicts(data["direction"]),
            np.array(data["visibility"]),
            np.array(data["keys"]) if data["keys"] is not None else None,
        )

    @staticmethod
    def ratio(vs, expected, zero_ends=True):
        avs, aex = np.abs(vs), np.abs(expected)

        nom = np.maximum(avs, aex)
        denom = np.minimum(avs, aex)
        denom = np.maximum(denom, nom / 10)

        with np.errstate(divide="ignore", invalid="ignore"):
            res = ((avs > aex) * 2 - 1) * (nom / denom - 1)

        res[vs * expected < 0] = -10
        if zero_ends:
            res[0] = 0
            res[-1] = 0
        return res

    def _pos_vis(loc: g.Point):
        """Accounts for how hard it is to see an error due to the distance from the pilot.
        Assumes distance is a function only of x and z position, not the y position.
        """
        res = abs(g.Point.vector_projection(loc, g.PY())) / abs(loc)
        return np.nan_to_num(res, nan=1)

    @staticmethod
    def _vector_vis(direction: g.Point, loc: g.Point) -> Union[g.Point, npt.NDArray]:
        # a vector error is more visible if it is perpendicular to the viewing vector
        # 0 to np.pi, pi/2 gives max, 0&np.pi give min
        return direction, (
            1 - 0.9 * np.abs(g.Point.cos_angle_between(loc, direction))
        ) * Measurement._pos_vis(loc)

    @staticmethod
    def _roll_vis(fl: State, tp: State) -> Union[g.Point, npt.NDArray]:
        afl = g.Point.cos_angle_between(fl.pos, fl.att.transform_point(g.PZ()))
        atp = g.Point.cos_angle_between(tp.pos, tp.att.transform_point(g.PZ()))

        azfl = np.cos(fl.att.inverse().transform_point(-fl.pos).planar_angles().x)
        aztp = np.cos(tp.att.inverse().transform_point(-tp.pos).planar_angles().x)

        ao = afl.copy()

        ao[np.abs(afl) > np.abs(atp)] = atp[np.abs(afl) > np.abs(atp)]
        ao[np.sign(azfl) != np.sign(aztp)] = (
            0  # wings have passed through the view vector
        )

        rvis = 1 - 0.9 * np.abs(ao)

        return fl.att.transform_point(g.PZ()), rvis * Measurement._pos_vis(fl.pos)

    @staticmethod
    def _pitch_vis(fl: State, tp: State) -> Union[g.Point, npt.NDArray]:
        rvis = 1 - 0.9 * np.abs(
            g.Point.cos_angle_between(fl.pos, fl.att.transform_point(g.PZ()))
        )

        return fl.att.transform_point(g.PZ()), rvis * Measurement._pos_vis(fl.pos)

    @staticmethod
    def _rad_vis(loc: g.Point, axial_dir: g.Point) -> Union[g.Point, npt.NDArray]:
        # radial error more visible if axis is parallel to the view vector
        return axial_dir, (
            0.2 + 0.8 * np.abs(g.Point.cos_angle_between(loc, axial_dir))
        ) * Measurement._pos_vis(loc)

    @staticmethod
    def _inter_scale_vis(fl: State):
        # factor of 1 when it takes up 1/2 of the box height.
        # reduces to zero for zero length el
        depth = fl.pos.y.mean()
        _range = fl.pos.max() - fl.pos.min()
        length = np.sqrt(_range.x[0] ** 2 + _range.z[0] ** 2)
        return min(1, length / (depth * 0.8660254))  # np.tan(np.radians(60)) / 2

    @staticmethod
    def speed_value(fl: State, tp: State, direction: g.Point = None) -> Self:
        if direction:
            body_direction = fl.att.inverse().transform_point(direction)
            return Measurement(
                g.Point.scalar_projection(fl.vel, body_direction),
                "m/s",
                *Measurement._vector_vis(
                    fl.att.transform_point(direction).unit(), fl.pos
                ),
            )
        else:
            value = abs(fl.vel)
            return Measurement(
                value,
                "m/s",
                *Measurement._vector_vis(fl.att.transform_point(fl.vel).unit(), fl.pos),
            )

    @staticmethod
    def vertical_speed(fl: State, tp: State) -> Self:
        return Measurement.speed_value(fl, tp, g.PZ())

    @staticmethod
    def speed(fl: State, tp: State) -> Measurement:
        return Measurement(
            fl.vel - fl.vel[0],
            "m/s",
            *Measurement._vector_vis(fl.att.transform_point(fl.vel).unit(), fl.pos),
        )

    @staticmethod
    def roll_angle(fl: State, tp: State) -> Self:
        """direction is the body X axis, value is equal to the roll angle difference from template"""
        body_roll_error = g.Quaternion.body_axis_rates(tp.att, fl.att) * g.PX()
        world_roll_error = fl.att.transform_point(body_roll_error)

        return Measurement(
            np.unwrap(abs(world_roll_error) * np.sign(body_roll_error.x)),
            "rad",
            *Measurement._roll_vis(fl, tp),
        )

    @staticmethod
    def roll_angle_proj(fl: State, tp: State, proj: g.Point) -> Self:
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

    @staticmethod
    def roll_angle_p(fl: State, tp: State) -> Self:
        return Measurement.roll_angle_proj(fl, tp, Measurement.get_proj(tp))

    @staticmethod
    def roll_angle_y(fl: State, tp: State) -> Self:
        return Measurement.roll_angle_proj(fl, tp, g.PY())

    @staticmethod
    def roll_angle_z(fl: State, tp: State) -> Self:
        return Measurement.roll_angle_proj(fl, tp, g.PZ())

    @staticmethod
    def length(fl: State, tp: State, direction: g.Point = None) -> Self:
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

    def stallturn_width(fl: State, tp: State) -> Measurement:
        return Measurement.length(fl, tp, g.PY())

    @staticmethod
    def roll_rate(fl: State, tp: State) -> Measurement:
        """ratio error, direction is vector in the body X axis, length is equal to the roll rate"""
        wrvel = abs(fl.att.transform_point(fl.p * g.PX())) * np.sign(fl.p)
        return Measurement(
            Measurement.ratio(wrvel, np.mean(wrvel)),
            "ratio",
            *Measurement._roll_vis(fl, tp),
        )

    @staticmethod
    def autorotation_rate(fl: State, tp: State) -> Measurement:
        p = abs(fl.att.transform_point(fl.p * g.PX())) * np.sign(fl.p)

        return Measurement(
            Measurement.ratio(p, np.mean(tp.p)),
            "ratio",
            fl.pos,
            Measurement._pos_vis(fl.pos),
        )

    @staticmethod
    def get_proj(tp: State):
        """Proj is a vector in the axial direction for the template ref_frame (tp[0].transform)*"""
        # proj = g.g.Point(0, np.cos(el.ke), np.sin(el.ke))
        return g.PX().cross(tp[0].arc_centre()).unit()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def track_y(fl: State, tp: State) -> Measurement:
        """angle error in the velocity vector about the template Z axis"""
        return Measurement.track_proj_ang(fl, tp, g.PZ())

    @staticmethod
    def track_z(fl: State, tp: State) -> Measurement:
        return Measurement.track_proj_ang(fl, tp, g.PY())

    @staticmethod
    def pitch_attitude(fl: State, tp: State) -> Measurement:
        fxvec = fl.att.transform_point(g.PX())
        tpvec = tp.att.transform_point(g.PX())

        xvec_tp = tp.att.inverse().transform_point(fxvec)

        return Measurement(
            np.arctan2(xvec_tp.z, xvec_tp.x),
            "rad",
            *Measurement._vector_vis(
                g.Point.vector_rejection(fxvec, tpvec).unit(), fl.pos
            ),
        )

    @staticmethod
    def yaw_attitude(fl: State, tp: State) -> Measurement:
        fxvec = fl.att.transform_point(g.PX())
        tpvec = tp.att.transform_point(g.PX())

        xvec_tp = tp.att.inverse().transform_point(fxvec)

        flturns = np.cumsum(fl.r * fl.dt) / (np.pi)
        tpturns = np.cumsum(tp.r * tp.dt) / (np.pi)

        return Measurement(
            np.round(flturns - tpturns) * np.pi + np.arctan2(xvec_tp.y, xvec_tp.x),
            "rad",
            *Measurement._vector_vis(
                g.Point.vector_rejection(fxvec, tpvec).unit(), fl.pos
            ),
        )

    @staticmethod
    def curvature(fl: State, tp: State, proj: g.Point) -> Measurement:
        """
        Ratio error in curvature, direction is a vector in the axial direction
        proj is the ref_frame(tp[0]) axial direction
        """
        wproj = tp[0].att.transform_point(proj)  # world proj vector

        trfl = fl.to_track()

        normal_acc = trfl.zero_g_acc() * g.Point(
            0, 1, 1
        )  # acceleration normal to velocity vector

        tp_acc = g.Point.vector_rejection(
            tp.zero_g_acc(), tp.att.inverse().transform_point(wproj)
        )  # acceleration in template axial direction

        with np.errstate(invalid="ignore"):
            c = (
                g.Point.scalar_projection(normal_acc, tp_acc) / abs(trfl.u) ** 2
            )  # acceleration in loop radial direction

        return Measurement(
            Measurement.ratio(c, abs(tp_acc / abs(tp.vel) ** 2)),
            "ratio",
            *Measurement._rad_vis(fl.pos, tp[0].att.transform_point(wproj)),
        )

    @staticmethod
    def curvature_proj(fl: State, tp: State) -> Measurement:
        return Measurement.curvature(fl, tp, Measurement.get_proj(tp))

    @staticmethod
    def depth_vis(loc: g.Point):
        """Accounts for how hard it is to tell whether the aircraft is at a downgradable
        distance (Y position). Assuming that planes look closer in the centre of the box than the end,
        even if they are at the same Y position.
        """
        rot = np.abs(np.arctan(loc.x / loc.y))
        return loc, 0.4 + 0.6 * rot / np.radians(60)

    @staticmethod
    def depth(fl: State) -> Measurement:
        return Measurement(fl.pos.y, "m", *Measurement.depth_vis(fl.pos))

    @staticmethod
    def lateral_pos_vis(loc: g.Point):
        """How hard is it for the judge tell the lateral position. Based on the following principals:
        - its easier when the plane is lower as its closer to the box markers. (1 for low, 0.5 for high)
        """
        r60 = np.radians(60)
        return loc, (0.5 + 0.5 * (r60 - np.abs(np.arctan(loc.z / loc.y))) / r60)

    @staticmethod
    def side_box(fl: State):
        return Measurement(
            np.arctan(fl.pos.x / fl.pos.y), "rad", *Measurement.lateral_pos_vis(fl.pos)
        )

    @staticmethod
    def top_box(fl: State):
        return Measurement(
            np.arctan(fl.pos.z / fl.pos.y),
            "rad",
            fl.pos,
            np.full(len(fl), 0.5),  # top box is always hard to tell
        )

    @staticmethod
    def centre_box(fl: State):
        return Measurement(
            np.arctan(fl.pos.x / fl.pos.y), "rad", *Measurement.lateral_pos_vis(fl.pos)
        )

    def alpha(fl: State, tp: State) -> Measurement:
        """Estimate alpha based on Z force"""
        alpha_acc = -4.6 * fl.acc.z / (abs(fl.vel) ** 2)  # 2.6
        return Measurement(alpha_acc, "rad", *Measurement._pitch_vis(fl, tp))

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

    def delta_alpha(fl: State, tp: State) -> Measurement:
        return Measurement(
            np.gradient(-4.6 * fl.acc.z / (abs(fl.vel) ** 2)) / fl.dt,
            "rad/s",
            *Measurement._pitch_vis(fl, tp),
        )

    def pitch_rate(fl: State, tp: State) -> Measurement:
        return Measurement(fl.q, "rad/s", *Measurement._pitch_vis(fl, tp))

    def pitch_down_rate(fl: State, tp: State) -> Measurement:
        return Measurement(
            fl.q * (fl.inverted().astype(int) * 2 - 1),
            "rad/s",
            *Measurement._pitch_vis(fl, tp),
        )

    def delta_p(fl: State, tp: State) -> Measurement:
        roll_direction = np.sign(fl.p.mean())
        return Measurement(
            roll_direction * np.gradient(fl.p) / fl.dt,
            "rad/s/s",
            *Measurement._pitch_vis(fl, tp),
        )
