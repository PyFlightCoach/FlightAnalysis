from __future__ import annotations
from flightdata import State
import geometry as g
import numpy as np
import pandas as pd
import numpy.typing as npt
from dataclasses import dataclass
from typing import Tuple
from flightanalysis.base.ref_funcs import RFuncBuilders


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
            visibility=self.visibility.tolist(),
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
            np.array(data["keys"]) if 'keys' in data and data["keys"] is not None else None,
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
        res = loc.y / abs(loc)
        return np.nan_to_num(res, nan=1)

    @staticmethod
    def _vector_vis(direction: g.Point, loc: g.Point) -> Tuple[g.Point, npt.NDArray]:
        # a vector error is more visible if it is perpendicular to the viewing vector
        # 0 to np.pi, pi/2 gives max, 0&np.pi give min
        return direction, (
            1 - 0.9 * np.abs(g.Point.cos_angle_between(loc, direction))
        ) * Measurement._pos_vis(loc)

    @staticmethod
    def _roll_vis(fl: State, tp: State) -> Tuple[g.Point, npt.NDArray]:
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
    def _pitch_vis(fl: State, tp: State) -> Tuple[g.Point, npt.NDArray]:
        rvis = 1 - 0.9 * np.abs(
            g.Point.cos_angle_between(fl.pos, fl.att.transform_point(g.PZ()))
        )

        return fl.att.transform_point(g.PZ()), rvis * Measurement._pos_vis(fl.pos)

    @staticmethod
    def _rad_vis(loc: g.Point, axial_dir: g.Point) -> Tuple[g.Point, npt.NDArray]:
        # radial error more visible if axis is parallel to the view vector
        return axial_dir, (
            0.2 + 0.8 * np.abs(g.Point.cos_angle_between(loc, axial_dir))
        ) * Measurement._pos_vis(loc)

    @staticmethod
    def _inter_scale_vis(fl: State, box):
        # factor of 1 when it takes up 1/2 of the box height.
        # reduces to zero for zero length el
        depth = fl.pos.y.mean()

        h = box.top_pos(g.PY(depth)) - box.bottom_pos(g.PY(depth))

        _range = fl.pos.max() - fl.pos.min()
        length = abs(_range)[0]
        return min(1, 2 * length / h.z[0])  # np.tan(np.radians(60)) / 2


    @staticmethod
    def get_axial_direction(tp: State):
        """Proj is a vector in the axial direction for the template ref_frame (tp[0].transform)*"""
        # proj = g.g.Point(0, np.cos(el.ke), np.sin(el.ke))
        return g.PX().cross(tp[0].arc_centre()).unit()

    @staticmethod
    def depth_vis(loc: g.Point):
        """Accounts for how hard it is to tell whether the aircraft is at a downgradable
        distance (Y position). Assuming that planes look closer in the centre of the box than the end,
        even if they are at the same Y position.
        """
        rot = np.abs(np.arctan(loc.x / loc.y))
        return loc, 0.4 + 0.6 * rot / np.radians(60)

    @staticmethod
    def lateral_pos_vis(loc: g.Point):
        """How hard is it for the judge tell the lateral position. Based on the following principals:
        - its easier when the plane is lower as its closer to the box markers. (1 for low, 0.5 for high)
        """
        r60 = np.radians(60)
        return loc, (0.5 + 0.5 * (r60 - np.abs(np.arctan(loc.z / loc.y))) / r60)



measures = RFuncBuilders({})