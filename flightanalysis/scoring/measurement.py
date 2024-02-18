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
    def speed(fl: State, tp: State, direction: Point=None, axis='body') -> Self:
        direction=Point(1,1,1) if direction is None else direction
        def get_body_direction(st: State):
            if axis == 'body':
                return direction
            else:
                world_direction = tp[0].transform.rotate(direction) if axis == 'ref_frame' else direction
                return st.att.inverse().transform_point(world_direction)
        body_direction = get_body_direction(fl)
        value = Point.scalar_projection(fl.vel, body_direction)
        
        return Measurement(
            value, 
            np.mean(Point.scalar_projection(tp.vel, get_body_direction(tp))),
            *Measurement._vector_vis(
                fl.att.transform_point(direction).unit(), 
                fl.pos
            )
        )

    @staticmethod
    def roll_angle(fl: State, tp: State) -> Self:
        """direction is the body X axis, value is equal to the roll angle difference from template"""
        body_roll_error = Quaternion.body_axis_rates(tp.att, fl.att) * PX()
        world_roll_error = fl.att.transform_point(body_roll_error)

        return Measurement(
            np.unwrap(abs(world_roll_error) * np.sign(body_roll_error.x)), 
            0, 
            *Measurement._roll_vis(fl.pos, fl.att)
        )

    @staticmethod
    def roll_angle_proj(fl: State, tp: State, proj: Point) -> Self:
        """Direction is the body X axis, value is equal to the roll angle error.
        roll angle error is the angle between the body proj vector axis and the 
        reference frame proj vector. 
        proj normal of the plane to measure roll angles against.

        """
        trfl = fl#.to_track() # flown in the track axis
        
        rfproj=tp[0].att.transform_point(proj) # proj vector in the ref_frame
        
        tr_rf_proj = trfl.att.inverse().transform_point(rfproj) # proj vector in track axis
        
        tp_rf_proj = tp.att.inverse().transform_point(rfproj) # proj vector in template body axis (body == track for template)
        
        with np.errstate(invalid='ignore'):
            fl_roll_angle = np.arcsin(Point.cross(tr_rf_proj, proj).x)
            tp_roll_angle = np.arcsin(Point.cross(tp_rf_proj, proj).x)
        


        return Measurement(
            fl_roll_angle - tp_roll_angle,
            0, 
            *Measurement._roll_vis(fl.pos, fl.att)
        )

    @staticmethod
    def roll_angle_y(fl: State, tp: State) -> Self:
        return Measurement.roll_angle_proj(fl, tp, PY())

    @staticmethod
    def roll_angle_z(fl: State, tp: State) -> Self:
        return Measurement.roll_angle_proj(fl, tp, PZ())

    @staticmethod
    def length(fl: State, tp: State, direction: Point=None) -> Self:
        '''Distance from the ref frame origin in the prescribed direction'''
        ref_frame = tp[0].transform
        distance = ref_frame.q.inverse().transform_point(fl.pos - ref_frame.pos) # distance in the ref_frame
        
        v = distance if direction is None else Point.vector_projection(distance, direction)

        return Measurement(
            Point.scalar_projection(v, direction), 0,
            *Measurement._vector_vis(ref_frame.q.transform_point(distance), fl.pos)
        )
            
    @staticmethod
    def roll_rate(fl: State, tp: State) -> Measurement:
        """vector in the body X axis, length is equal to the roll rate"""
        wrvel = fl.att.transform_point(fl.p * PX())
        return Measurement(abs(wrvel) * np.sign(fl.p), np.mean(tp.p), *Measurement._roll_vis(fl.pos, fl.att))
    
    @staticmethod
    def track_proj(fl: State, tp: State, proj: Point, fix='ang'):
        """
        Direction is the world frame scalar rejection of the velocity difference onto the template velocity 
        vector.
        proj defines the axis in the ref_frame (tp[0].transform) to work on.
        if fix=='vel' we are only interested in velocity errors in the proj vector. (loop axial track)
        if fix=='ang' we are only interested in angle errors about the proj vector. (loop exit track)
        """
        ref_frame = tp[0].transform
        tr = ref_frame.q.inverse()

        fwvel = fl.att.transform_point(fl.vel)
        twvel = tp.att.transform_point(tp.vel)

        direction, vis = Measurement._vector_vis(Point.vector_rejection(fwvel, twvel).unit(), fl.pos)
        
        fcvel = tr.transform_point(fwvel)
        tcvel = tr.transform_point(twvel)
        
        if fix == 'vel':
            verr = Point.vector_projection(fcvel, proj)
            sign = -np.ones_like(verr.x)
            sign[Point.is_parallel(verr, proj)] = 1
            
            angles = sign * np.arctan(abs(verr) / abs(fl.vel))
            
            vis = np.linspace(vis[0], vis[1], len(vis))
        elif fix == 'ang':
            cos_angles = Point.scalar_projection(Point.cross(fcvel, tcvel) / (abs(fcvel) * abs(tcvel)), proj)
            angles = np.arcsin(cos_angles)
        else:
            raise AttributeError(f'fix must be "vel" or "ang", not {fix}')
        return Measurement(angles, 0, direction, vis)

    @staticmethod
    def track_y(fl: State, tp:State) -> Measurement:
        """angle error in the velocity vector about the template Z axis"""
        return Measurement.track_proj(fl, tp, PZ())

    @staticmethod
    def track_z(fl: State, tp: State) -> Measurement:
        return Measurement.track_proj(fl, tp, PY())

    @staticmethod
    def radius(fl:State, tp:State, proj: Point) -> Measurement:
        """
        Error in radius as a vector in the radial direction
        proj is the ref_frame(tp[0]) axial direction
        """
        wproj = tp[0].att.transform_point(proj)
        
        trfl = fl.to_track()
        
        trproj = trfl.att.inverse().transform_point(wproj)
        
        normal_acc = trfl.zero_g_acc() * Point(0,1,1)
        
        with np.errstate(invalid='ignore'):
            r = trfl.u**2 / abs(Point.vector_rejection(normal_acc, trproj))
            
#        r = np.minimum(r, 400)
        return Measurement(
            r, np.mean(r), 
            *Measurement._rad_vis(
                fl.pos, 
                tp[0].att.transform_point(wproj)
            )  
        )
        
    @staticmethod
    def curvature(fl:State, tp:State, proj: Point) -> Measurement:
        """
        Error in curvature, direction is a vector in the axial direction
        proj is the ref_frame(tp[0]) axial direction
        """
        wproj = tp[0].att.transform_point(proj)
        
        trfl = fl.to_track()
        
        trproj = trfl.att.inverse().transform_point(wproj)
        
        normal_acc = trfl.zero_g_acc() * Point(0,1,1)
        
        with np.errstate(invalid='ignore'):
            c = abs(Point.vector_rejection(normal_acc, trproj)) / trfl.u**2
            
#        r = np.minimum(r, 400)
        return Measurement(
            c, np.mean(c), 
            *Measurement._rad_vis(
                fl.pos, 
                tp[0].att.transform_point(wproj)
            )  
        )
    
    @staticmethod
    def turns(fl: State, tp: State) -> Measurement:
        fl_turns = fl.rvel.cumsum() * fl.dt
        tp_turns = tp.rvel.cumsum() * fl.dt
        