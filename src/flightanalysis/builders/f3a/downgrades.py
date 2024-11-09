from flightanalysis.scoring.measurements import measures
from flightanalysis.scoring.downgrade import DownGrades, dg
from flightanalysis.scoring.selectors import selectors as sels
from flightanalysis.scoring.smoothing import smoothers as sms

from flightanalysis.builders.f3a.criteria import F3A
import numpy as np
from flightdata import State
from flightanalysis.elements import Loop, Line, Snap, Spin, StallTurn


def dg_applicator(el: Loop | Line | Snap | Spin | StallTurn, tp: State, last_kind: object, next_kind: object ):
    dgs = []

    if el.__class__ is Line:
        if abs(el.roll) > 0:
            dgs.append(dg("roll_angle", measures.roll_angle(), None, sels.last(), F3A.intra.end_roll))
        else:
            dgs.append(dg("roll_angle", measures.roll_angle(), sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll))
        if max(tp.pos.z) - min(tp.pos.z) < 1:
            if next_kind is Spin:
                dgs.append(dg("yaw_after_slowdown", measures.heading_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track))
                if el.uid == 'entry_line':
                    dgs.append(dg("last_heading_before_slowdown", measures.heading_track(), sms.lowpass(cutoff=4, order=5), [sels.before_slowdown(sp=13), sels.last()], F3A.intra.end_track))
                else:
                    dgs.append(dg("heading_before_slowdown", measures.heading_track(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.end_track))
            else:
                if el.uid == 'entry_line':
                    dgs.append(dg("heading", measures.heading_track(), None, sels.last(), F3A.intra.end_track))
                else:
                    dgs.append(dg("heading", measures.heading_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track))
            if el.uid != 'entry_line':
                dgs.append(dg("climb", measures.climb_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track))
            else:
                dgs.append(dg("climb", measures.climb_track(), None, sels.last(), F3A.intra.end_track))
        else:
            if next_kind is StallTurn:
                dgs.append(dg("track_y_before_slowdown", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.track))
                dgs.append(dg("track_z_before_slowdown", measures.rf_z_track(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.track))
                dgs.append(dg("pitch_after_slowdown", measures.pitch_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track))
                dgs.append(dg("yaw_after_slowdown", measures.yaw_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track))
            elif last_kind is StallTurn:
                dgs.append(dg("initial_track_y_after_speedup", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), [sels.after_speedup(sp=13), sels.first()], F3A.intra.end_track))
                dgs.append(dg("initial_track_z_after_speedup", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), [sels.after_speedup(sp=13), sels.first()], F3A.intra.end_track))
                dgs.append(dg("track_y_after_speedup", measures.rf_y_track(), sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=13), F3A.intra.track))
                dgs.append(dg("track_z_after_speedup", measures.rf_z_track(), sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=13), F3A.intra.track))
            else:
                dgs.append(dg("track_z", measures.rf_z_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track))
                dgs.append(dg("track_y", measures.rf_y_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track))
        
    elif el.__class__ is Loop:
        dgs.append(dg("roundness", measures.curvature_proj(), sms.curvature_lowpass(order=5), None, F3A.intra.loopshape))
        dgs.append(dg("smoothness", measures.absolute_curvature_proj(), sms.lowpass(cutoff=2, order=5), sels.borders(tb=0.25), F3A.intra.loopsmoothness))
        dgs.append(dg("axial_track", measures.loop_axial_track(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track))
        dgs.append(dg("radial_track", measures.loop_radial_track(), sms.lowpass(cutoff=2, order=5), sels.last(), F3A.intra.end_track))
        if el.roll == 0:
            dgs.append(dg("roll_angle", measures.roll_angle_p(), sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll))
        else:
            dgs.append(dg("roll_angle", measures.roll_angle_p(), None, sels.last(), F3A.intra.roll))
    elif el.__class__ is StallTurn:
        dgs.append(dg("width", measures.stallturn_width(), None, None, F3A.intra.stallturn_width))
        dgs.append(dg("speed", measures.vertical_speed(), None, sels.first_and_last(), F3A.intra.stallturn_speed))
        dgs.append(dg("roll_angle", measures.roll_angle_z(), None, None, F3A.intra.roll))
        dgs.append(dg("end_yaw", measures.yaw_attitude(), None, sels.last(), F3A.intra.end_track))
    elif el.__class__ is Spin:
        dgs.append(dg("turns", measures.roll_angle_y(), None, sels.last(), F3A.intra.end_roll))
        dgs.append(dg("alpha", measures.spin_alpha_f3a(), None, sels.before_recovery(rot=np.pi/4), F3A.intra.pos_autorotation_alpha))
        dgs.append(dg("drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), F3A.intra.drop_pitch_rate ))
        dgs.append(dg("peak_drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), F3A.intra.peak_drop_pitch_rate ))
        dgs.append(dg("exit_y_track", measures.loop_radial_track(), None, sels.last(), F3A.intra.end_track))
        dgs.append(dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), F3A.intra.recovery_roll_rate ))
    elif el.__class__ is Snap:
        dgs.append(dg("turns", measures.roll_angle_y(), None, sels.last(), F3A.intra.end_roll))
        dgs.append(dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), F3A.intra.recovery_roll_rate ))
        dgs.append(dg("alpha", measures.alpha_f3a(), None, sels.autorotation(brot=np.pi/4, rrot=np.pi/2), F3A.intra.autorotation_alpha))
        if last_kind is not Snap:
            dgs.append(dg("peak_break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), F3A.intra.peak_break_pitch_rate ))
            dgs.append(dg("break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), F3A.intra.break_pitch_rate ))
    if (el.__class__ is Line or el.__class__ is Loop ):
        if el.roll > 0:
            dgs.append(dg("roll_rate", measures.roll_rate(), sms.rollrate_lowpass(order=5), None, F3A.intra.rollrate))
            dgs.append(dg("roll_smoothness", measures.abs_roll_rate(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.rollsmoothness))
        if el.uid!='entry_line' and next_kind is not StallTurn  and next_kind is not Spin:
            dgs.append(dg("speed", measures.speed(), sms.lowpass(cutoff=0.5, order=5), None, F3A.intra.speed)) 


    return DownGrades(dgs)