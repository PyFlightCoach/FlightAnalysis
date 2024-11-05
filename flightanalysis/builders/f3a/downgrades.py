from flightanalysis.scoring.measurements import measures
from flightanalysis.scoring.downgrade import DownGrades, dg
from flightanalysis.scoring.selectors import selectors as sels
from flightanalysis.scoring.smoothing import smoothers as sms

from flightanalysis.builders.f3a.criteria import F3A
import numpy as np
from flightdata import State
from flightanalysis.elements import Loop, Line, Snap, Spin, StallTurn


line_roll_angle_end = dg("roll_angle", measures.roll_angle(), None, sels.last(), F3A.intra.end_roll)
line_roll_angle = dg("roll_angle", measures.roll_angle(), sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll)
line_roll_angle_gradient = dg("roll_rate", measures.roll_angle_gradient(), sms.lowpass(cutoff=1.5, order=5), sels.middle(chopt=0.2), F3A.intra.roll_gradient)
line_yaw_pre_spin = dg("yaw_after_slowdown", measures.heading_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track)
line_track_pre_spin_end = dg("last_heading_before_slowdown", measures.heading_track(), sms.lowpass(cutoff=4, order=5), [sels.before_slowdown(sp=13), sels.last()], F3A.intra.end_track)
line_track_pre_spin = dg("heading_before_slowdown", measures.heading_track(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.end_track)
line_track_end = dg("heading", measures.heading_track(), None, sels.last(), F3A.intra.end_track)
line_track = dg("heading", measures.heading_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track)
line_climb = dg("climb", measures.climb_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track)
line_climb_end = dg("climb", measures.climb_track(), None, sels.last(), F3A.intra.end_track)

stallturn_track_y_before_slowdown = dg("track_y_before_slowdown", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.track)
stallturn_track_z_before_slowdown = dg("track_z_before_slowdown", measures.rf_z_track(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.track)
stallturn_pitch_after_slowdown = dg("pitch_after_slowdown", measures.pitch_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track)
stallturn_yaw_after_slowdown = dg("yaw_after_slowdown", measures.yaw_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track)

stallturn_initial_track_y_after_speedup = dg("initial_track_y_after_speedup", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), [sels.after_speedup(sp=13), sels.first()], F3A.intra.end_track)
stallturn_initial_track_z_after_speedup = dg("initial_track_z_after_speedup", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), [sels.after_speedup(sp=13), sels.first()], F3A.intra.end_track)
stallturn_track_y_after_speedup = dg("track_y_after_speedup", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=13), F3A.intra.track)
stallturn_track_z_after_speedup = dg("track_z_after_speedup", measures.rf_z_track(), sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=13), F3A.intra.track)

line_track_z = dg("track_z", measures.rf_z_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track)
line_track_y = dg("track_y", measures.rf_y_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track)

loop_roundness = dg("roundness", measures.curvature_proj(), sms.curvature_lowpass(order=5, cut=4), None, F3A.intra.loopshape)
loop_smoothness = dg("smoothness", measures.loop_smoothness_proj(), sms.lowpass(cutoff=0.75, order=3), sels.middle(chopt=0.25), F3A.intra.loopsmoothness)
loop_axial_track = dg("axial_track", measures.loop_axial_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track)
loop_radial_track = dg("radial_track", measures.loop_radial_track(), sms.lowpass(cutoff=2, order=5), sels.last(), F3A.intra.end_track)

loop_roll_angle = dg("roll_angle", measures.roll_angle_p(), sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll)
loop_roll_angle_end = dg("roll_angle", measures.roll_angle_p(), None, sels.last(), F3A.intra.roll)
loop_roll_angle_gradient = dg("roll_rate", measures.roll_angle_p_gradient(), sms.lowpass(cutoff=1.5, order=5), None, F3A.intra.roll_gradient)

stallturn_width = dg("width", measures.stallturn_width(), None, None, F3A.intra.stallturn_width)
stallturn_speed = dg("speed", measures.vertical_speed(), None, sels.first_and_last(), F3A.intra.stallturn_speed)
stallturn_roll_angle = dg("roll_angle", measures.roll_angle_z(), None, None, F3A.intra.roll)
stallturn_end_yaw = dg("end_yaw", measures.yaw_attitude(), None, sels.last(), F3A.intra.end_track)

stallturn_turns = dg("turns", measures.roll_angle_y(), None, sels.last(), F3A.intra.end_roll)
stallturn_alpha = dg("alpha", measures.spin_alpha_f3a(), None, sels.before_recovery(rot=np.pi/4), F3A.intra.pos_autorotation_alpha)
stallturn_drop_pitch_rate = dg("drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), F3A.intra.drop_pitch_rate )
stallturn_peak_drop_pitch_rate = dg("peak_drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), F3A.intra.peak_drop_pitch_rate )
stallturn_exit_y_track = dg("exit_y_track", measures.loop_radial_track(), None, sels.last(), F3A.intra.end_track)
stallturn_recovery_rate_delta = dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), F3A.intra.recovery_roll_rate )

snap_turns = dg("turns", measures.roll_angle_y(), None, sels.last(), F3A.intra.end_roll)
snap_recovery_rate_delta = dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), F3A.intra.recovery_roll_rate )
snap_alpha = dg("alpha", measures.alpha_f3a(), None, sels.autorotation(brot=np.pi/4, rrot=np.pi/2), F3A.intra.autorotation_alpha)

snap_peak_break_pitch_rate = dg("peak_break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), F3A.intra.peak_break_pitch_rate )
snap_break_pitch_rate = dg("break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), F3A.intra.break_pitch_rate )

roll_rate = dg("roll_rate", measures.roll_rate(), sms.rollrate_lowpass(order=5), None, F3A.intra.rollrate)
roll_smoothness = dg("roll_smoothness", measures.abs_roll_rate(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.rollsmoothness)

speed = dg("speed", measures.speed(), sms.lowpass(cutoff=0.5, order=5), None, F3A.intra.speed)


def dg_applicator(el: Loop | Line | Snap | Spin | StallTurn, tp: State, last_kind: object, next_kind: object ):
    dgs = []

    if el.__class__ is Line:
        if abs(el.roll) > 0:
            dgs.append(line_roll_angle_end)
        else:
            dgs.append(line_roll_angle)
            dgs.append(line_roll_angle_gradient)
        if max(tp.pos.z) - min(tp.pos.z) < 1:
            if next_kind is Spin:
                dgs.append(line_yaw_pre_spin)
                if el.uid == 'entry_line':
                    dgs.append(line_track_pre_spin_end)
                else:
                    dgs.append(line_track_pre_spin)
            else:
                if el.uid == 'entry_line':
                    dgs.append(line_track_end)
                else:
                    dgs.append(line_track)
            if el.uid != 'entry_line':
                dgs.append(line_climb)
            else:
                dgs.append(line_climb_end)
        else:
            if next_kind is StallTurn:
                dgs.append(stallturn_track_y_before_slowdown)
                dgs.append(stallturn_track_z_before_slowdown)
                dgs.append(stallturn_pitch_after_slowdown)
                dgs.append(stallturn_yaw_after_slowdown)
            elif last_kind is StallTurn:
                dgs.append(stallturn_initial_track_y_after_speedup)
                dgs.append(stallturn_initial_track_z_after_speedup)
                dgs.append(stallturn_track_y_after_speedup)
                dgs.append(stallturn_track_z_after_speedup)
            else:
                dgs.append(line_track_z)
                dgs.append(line_track_y)
        
    elif el.__class__ is Loop:
        dgs.append(loop_roundness)
        dgs.append(loop_smoothness)
        dgs.append(loop_axial_track)
        dgs.append(loop_radial_track)
        if el.roll == 0:
            dgs.append(loop_roll_angle)
            dgs.append(loop_roll_angle_gradient)
        else:
            dgs.append(loop_roll_angle_end)
    elif el.__class__ is StallTurn:
        dgs.append(stallturn_width)
        dgs.append(stallturn_speed)
        dgs.append(stallturn_roll_angle)
        dgs.append(stallturn_end_yaw)
    elif el.__class__ is Spin:
        dgs.append(stallturn_turns)
        dgs.append(stallturn_alpha)
        dgs.append(stallturn_drop_pitch_rate)
        dgs.append(stallturn_peak_drop_pitch_rate)
        dgs.append(stallturn_exit_y_track)
        dgs.append(stallturn_recovery_rate_delta)
    elif el.__class__ is Snap:
        dgs.append(snap_turns)
        dgs.append(snap_recovery_rate_delta)
        dgs.append(snap_alpha)
        if last_kind is not Snap:
            dgs.append(snap_peak_break_pitch_rate)
            dgs.append(snap_break_pitch_rate)
    if (el.__class__ is Line or el.__class__ is Loop ):
        if el.roll > 0:
            dgs.append(roll_rate)
            dgs.append(roll_smoothness)
        if el.uid!='entry_line' and next_kind is not StallTurn  and next_kind is not Spin:
            dgs.append(speed) 


    return DownGrades(dgs)