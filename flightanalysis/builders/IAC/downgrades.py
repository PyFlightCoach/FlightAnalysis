from flightanalysis.scoring.measurements import measures, Measurement
from flightanalysis.scoring.downgrade import DownGrades, dg
from flightanalysis.scoring.selectors import selectors as sels
from flightanalysis.scoring.smoothing import smoothers as sms
from flightanalysis.builders.IAC.criteria import IAC
import numpy as np
from flightdata import State
from flightanalysis.elements import Loop, Line, Snap, Spin, StallTurn
import geometry as g

#LINES
#                                   track Y              Track Z
# if vel is horizontal:             heading attitude     altitude track
# if vel is not horizontal:         RF Y attitude        RF Z attitude

#LOOPS
#if axial direction vertical:       axial track
#if axial direction not vertical:   axial attitude       
#      if exit vel horizontal:                           exit radial track
#      if exit vel not horizontal:                       exit radial attitude


line_roll_angle_end = dg("roll_angle", measures.roll_angle(), None, sels.last(), IAC.intra.end_roll)
line_roll_angle = dg("roll_angle", measures.roll_angle(), sms.lowpass(cutoff=1, order=5), None, IAC.intra.roll)
line_heading_horiz = dg("heading", measures.heading_track(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track)
line_climb_horiz = dg("climb", measures.climb_track(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track)
line_pitch_attitude = dg("pitch", measures.pitch_attitude(), None, None, IAC.intra.track)
line_yaw_attitude = dg("yaw", measures.yaw_attitude(), None, None, IAC.intra.track)

loop_roundness = dg("roundness", measures.curvature_proj(), sms.curvature_lowpass(order=5, cut=4), None, IAC.intra.loopshape)
loop_smoothness = dg("smoothness", measures.loop_smoothness_proj(), sms.lowpass(cutoff=2, order=5), sels.middle(chopt=0.5), IAC.intra.loopsmoothness)
loop_axial_track = dg("axial_track", measures.loop_axial_track(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track)
loop_axial_attitude = dg("axial_attitude", measures.loop_axial_attitude(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track)
loop_radial_track = dg("radial_track", measures.loop_radial_track(), sms.lowpass(cutoff=2, order=5), sels.last(), IAC.intra.end_track)
loop_radial_attitude = dg("radial_attitude", measures.loop_radial_attitude(), sms.lowpass(cutoff=2, order=5), sels.last(), IAC.intra.end_track)
loop_roll_angle = dg("roll_angle", measures.roll_angle_p(), sms.lowpass(cutoff=1, order=5), None, IAC.intra.roll)
loop_end_roll_angle = dg("roll_angle", measures.roll_angle_p(), None, sels.last(), IAC.intra.roll)

stallturn_width = dg("width", measures.stallturn_width(), None, None, IAC.intra.stallturn_width)
stallturn_speed = dg("speed", measures.vertical_speed(), None, sels.first_and_last(), IAC.intra.stallturn_speed)
stallturn_roll_angle = dg("roll_angle", measures.roll_angle_z(), None, None, IAC.intra.roll)
stallturn_end_yaw = dg("end_yaw", measures.yaw_attitude(), None, sels.last(), IAC.intra.end_track)

spin_turns = dg("turns", measures.roll_angle_y(), None, sels.last(), IAC.intra.end_roll)
spin_alpha = dg("alpha", measures.spin_alpha_iac(), None, sels.before_recovery(rot=np.pi/4), IAC.intra.pos_autorotation_alpha)
spin_drop_pitch_rate = dg("drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), IAC.intra.drop_pitch_rate )
spin_peak_drop_pitch_rate = dg("peak_drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), IAC.intra.peak_drop_pitch_rate )
spin_exit_y_track = dg("exit_y_track", measures.loop_radial_track(), None, sels.last(), IAC.intra.end_track)
spin_recovery_rate_delta = dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), IAC.intra.recovery_roll_rate )

snap_turns = dg("turns", measures.roll_angle_y(), None, sels.last(), IAC.intra.end_roll)
snap_recovery_rate_delta = dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), IAC.intra.recovery_roll_rate )
snap_alpha = dg("alpha", measures.alpha_iac(), None, sels.autorotation(brot=np.pi/4, rrot=np.pi/2), IAC.intra.autorotation_alpha)
snap_peak_break_pitch_rate = dg("peak_break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), IAC.intra.peak_break_pitch_rate )
snap_break_pitch_rate = dg("break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), IAC.intra.break_pitch_rate )

roll_rate = dg("roll_rate", measures.roll_rate(), sms.rollrate_lowpass(order=5), None, IAC.intra.rollrate)
roll_smoothness = dg("roll_smoothness", measures.abs_roll_rate(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.rollsmoothness)


def dg_applicator(el: Loop | Line | Snap | Spin | StallTurn, tp: State, last_kind: object, next_kind: object ):
    dgs = []

    if el.__class__ is Line:
        if abs(el.roll) > 0:
            dgs.append(line_roll_angle_end)
        else:
            dgs.append(line_roll_angle)
        if max(tp.pos.z) - min(tp.pos.z) < 1:
            dgs.append(line_heading_horiz)
            dgs.append(line_climb_horiz)
        else:
            dgs.append(line_pitch_attitude)
            dgs.append(line_yaw_attitude)
    elif el.__class__ is Loop:
        dgs.append(loop_roundness)
        dgs.append(loop_smoothness)
        isCircle = g.point.is_parallel(Measurement.get_axial_direction(tp), g.PZ())
        if isCircle:
            dgs.append(loop_axial_track)
        else:
            dgs.append(loop_axial_attitude)
        if abs(tp.vel[-1].z[0]) < 1:
            dgs.append(loop_radial_track)
        else:
            dgs.append(loop_radial_attitude)
        if el.roll == 0:
            dgs.append(loop_roll_angle)
        else:
            dgs.append(loop_end_roll_angle)
    elif el.__class__ is StallTurn:
        dgs.append(stallturn_width)
        dgs.append(stallturn_speed)
        dgs.append(stallturn_roll_angle)
        dgs.append(stallturn_end_yaw)
    elif el.__class__ is Spin:
        dgs.append(spin_turns)
        dgs.append(spin_alpha)
        dgs.append(spin_drop_pitch_rate)
        dgs.append(spin_peak_drop_pitch_rate)
        dgs.append(spin_exit_y_track)
        dgs.append(spin_recovery_rate_delta)
    elif el.__class__ is Snap:
        dgs.append(snap_turns)
        dgs.append(snap_recovery_rate_delta)
        dgs.append(snap_alpha)
        if last_kind is not Snap:
            dgs.append(snap_peak_break_pitch_rate)
            dgs.append(snap_break_pitch_rate)
    if (el.__class__ is Line or el.__class__ is Loop ):
        if abs(el.roll) > 0:
            dgs.append(roll_rate)
            dgs.append(roll_smoothness)
        

    return DownGrades(dgs)
