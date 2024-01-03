from __future__ import annotations
from flightdata import State
from geometry import Point, Quaternion, PX, PY, PZ, P0, Transformation
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from typing import Union, Any, Self



@dataclass()
class Measurement:
    value: npt.NDArray
    expected: float
    direction: Point
    visibility: npt.NDArray

    def __len__(self):
        return len(self.value)

    def __getitem__(self, sli):
        return Measurement(
            self.value[sli], 
            self.expected,
            self.direction[sli],
            self.visibility[sli],
        )

    def to_dict(self):
        return dict(
            value = list(self.value),
            expected = self.expected,
            direction = self.direction.to_dict(),
            visibility = list(self.visibility)
        )
    
    def exit_only(self):
        fac = np.zeros(len(self.value))
        fac[-1] = 1
        return Measurement(
            self.value * fac,
            self.expected,
            self.direction,
            self.visibility * fac
        )

    @staticmethod
    def from_dict(data) -> Measurement:
        return Measurement(
            np.array(data['value']),
            data['expected'],
            Point.from_dict(data['direction']),
            np.array(data['visibility'])
        )

    def _pos_vis(loc: Point):
        return abs(Point.vector_rejection(loc, PY())) / abs(loc)

    @staticmethod
    def _vector_vis(direction: Point, loc: Point) -> Union[Point, npt.NDArray]:
        #a vector error is more visible if it is perpendicular to the viewing vector
        # 0 to np.pi, pi/2 gives max, 0&np.pi give min
        return direction,  (1 - 0.8* np.abs(Point.cos_angle_between(loc, direction))) * Measurement._pos_vis(loc)

    @staticmethod
    def _roll_vis(loc: Point, att: Quaternion) -> Union[Point, npt.NDArray]:
        #a roll error is more visible if the movement of the wing tips is perpendicular to the view vector
        #the wing tips move in the local body Z axis
        world_tip_movement_direction = att.transform_point(PZ()) 
        return world_tip_movement_direction, (1-0.8*np.abs(Point.cos_angle_between(loc, world_tip_movement_direction))) * Measurement._pos_vis(loc)

    @staticmethod
    def _rad_vis(loc:Point, axial_dir: Point) -> Union[Point, npt.NDArray]:
        #radial error more visible if axis is parallel to the view vector
        return axial_dir, (0.2+0.8*np.abs(Point.cos_angle_between(loc, axial_dir))) * Measurement._pos_vis(loc)

    @staticmethod
    def speed(fl: State, tp: State, ref_frame: Transformation) -> Self:
        wvel = fl.att.transform_point(fl.vel) 
        spd = abs(wvel)
        return Measurement(spd, np.mean(spd),*Measurement._vector_vis(wvel.unit(), fl.pos))
    
    @staticmethod
    def roll_angle(fl: State, tp: State, ref_frame: Transformation) -> Self:
        """direction is the body X axis, value is equal to the roll angle difference from template"""
        body_roll_error = Quaternion.body_axis_rates(tp.att, fl.att) * PX()
        world_roll_error = fl.att.transform_point(body_roll_error)

        return Measurement(
            np.unwrap(abs(world_roll_error) * np.sign(body_roll_error.x)), 
            0, 
            *Measurement._roll_vis(fl.pos, fl.att)
        )

    @staticmethod
    def roll_angle_proj(fl: State, tp: State, ref_frame: Transformation, proj: Point) -> Self:
        """Direction is the body X axis, value is equal to the roll angle error.
        roll angle error is the angle between the body proj vector axis and the 
        reference frame proj vector. Proj vector should usually be defined by the ke angle of the loop. 
        """
        world_refframe_plane = ref_frame.q.transform_point(proj)
        world_body_plane = fl.att.transform_point(proj)
        
        angles = Point.vector_rejection(world_body_plane, world_refframe_plane).arctan
        
        return Measurement(
            abs(angles),
            0, 
            *Measurement._roll_vis(fl.pos, fl.att)
        )

    @staticmethod
    def roll_angle_y(fl: State, tp: State, ref_frame: Transformation) -> Self:
        return Measurement.roll_angle_proj(fl, tp, ref_frame, PY())

    @staticmethod
    def roll_angle_z(fl: State, tp: State, ref_frame: Transformation) -> Self:
        return Measurement.roll_angle_proj(fl, tp, ref_frame, PZ())

    @staticmethod
    def length_above(fl: State, tp: State, ref_frame: Transformation, direction: Point=None, free:float=0) -> Self:
        '''Distance from the ref frame origin in the prescribed direction above a free amount'''
        distance = ref_frame.q.inverse().transform_point(fl.pos - ref_frame.pos)
        
        v = distance if direction is None else Point.vector_projection(distance, direction)
        av = abs(v)
        vo = np.zeros_like(av) 
        sign = -np.ones_like(av)
        sign[Point.is_parallel(v, direction)] = 1
        vo[av>free] = (sign * (av - free))[av>free]
        return Measurement(
            vo, 0,
            *Measurement._vector_vis(ref_frame.q.transform_point(distance), fl.pos)
        )
            
    @staticmethod
    def roll_rate(fl: State, tp: State, ref_frame: Transformation) -> Measurement:
        """vector in the body X axis, length is equal to the roll rate"""
        wrvel = fl.att.transform_point(fl.p * PX())
        return Measurement(abs(wrvel) * np.sign(fl.p), np.mean(fl.p), *Measurement._roll_vis(fl.pos, fl.att))
    
    @staticmethod
    def track_y(fl: State, tp:State, ref_frame: Transformation) -> Measurement:
        """angle error in the velocity vector about the coord y axis"""
        tr = ref_frame.q.inverse()
        
        fcvel = tr.transform_point(fl.att.transform_point(fl.vel)) #flown ref frame vel
        tcvel = tr.transform_point(tp.att.transform_point(tp.vel)) # template ref frame vel

        cverr = Point.vector_rejection(fcvel, tcvel)
        wverr = ref_frame.q.transform_point(cverr)

        angle_err = np.arcsin(cverr.y / abs(fl.vel) )

        wz_angle_err = fl.att.transform_point(PZ() * angle_err)

        return Measurement(np.unwrap(abs(wz_angle_err) * np.sign(angle_err)), 0, *Measurement._vector_vis(wverr.unit(), fl.pos))

    @staticmethod
    def track_z(fl: State, tp: State, ref_frame: Transformation) -> Measurement:
        tr = ref_frame.q.inverse()
        
        fcvel = tr.transform_point(fl.att.transform_point(fl.vel)) #flown ref frame vel
        tcvel = tr.transform_point(tp.att.transform_point(tp.vel)) # template ref frame vel

        cverr = Point.vector_rejection(fcvel, tcvel)
        wverr = ref_frame.q.transform_point(cverr)

        angle_err = np.arcsin(cverr.z / abs(fl.vel) )

        wz_angle_err = fl.att.transform_point(PY() * angle_err)

        return Measurement(np.unwrap(abs(wz_angle_err) * np.sign(angle_err)), 0, *Measurement._vector_vis(wverr.unit(), fl.pos))

    @staticmethod
    def radius(fl:State, tp:State, ref_frame: Transformation) -> Measurement:
        """error in radius as a vector in the radial direction"""
        flrad = fl.arc_centre() 

        fl_loop_centre = fl.body_to_world(flrad)  # centre of loop in world frame
        tr = ref_frame.att.inverse()
        fl_loop_centre_lc = tr.transform_point(fl_loop_centre - ref_frame.pos)

        #figure out whether its a KE loop
        loop_plane = PY()
        tp_lc = tp.move_back(ref_frame)
        fl_lc = fl.move_back(ref_frame)
        if (tp_lc.y.max() - tp_lc.y.min()) > (tp_lc.z.max() - tp_lc.z.min()):
            loop_plane = PZ()
        
        #loop frame radius vector
        fl_rad_lc = Point.vector_rejection(fl_loop_centre_lc, loop_plane) - fl_lc.pos 
        
        ab = np.nan_to_num(abs(fl_rad_lc), nan=1000)
        return Measurement(
            ab, np.mean(ab), 
            *Measurement._rad_vis(
                fl.pos, 
                ref_frame.att.transform_point(loop_plane)
            )  
        )