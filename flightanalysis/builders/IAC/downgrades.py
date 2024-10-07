from flightanalysis.scoring.measurements import measures, Measurement
from flightanalysis.scoring.downgrade import DownGrades, dg, DowgradeGroups
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



def dg_applicator(el: Loop | Line | Snap | Spin | StallTurn, tp: State, last_kind: object, next_kind: object ):
    dgs = []

    if el.__class__ is Line:
        if abs(el.roll) > 0:
            dgs.append(dg("roll_angle", measures.roll_angle(), None, sels.last(), IAC.intra.end_roll))
        else:
            dgs.append(dg("roll_angle", measures.roll_angle(), sms.lowpass(cutoff=1, order=5), None, IAC.intra.roll))
        if max(tp.pos.z) - min(tp.pos.z) < 1:
            dgs.append(dg("heading", measures.heading_track(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track))
            dgs.append(dg("climb", measures.climb_track(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track))
        else:
            dgs.append(dg("pitch", measures.pitch_attitude(), None, None, IAC.intra.track))
            dgs.append(dg("yaw", measures.yaw_attitude(), None, None, IAC.intra.track))
    elif el.__class__ is Loop:
        dgs.append(dg("roundness", measures.curvature_proj(), sms.curvature_lowpass(order=5), None, IAC.intra.loopshape))
        dgs.append(dg("smoothness", measures.absolute_curvature_proj(), sms.lowpass(cutoff=2, order=5), sels.borders(tb=0.25), IAC.intra.loopsmoothness))
        isCircle = g.point.is_parallel(Measurement.get_axial_direction(tp), g.PZ())
        if isCircle:
            dgs.append(dg("axial_track", measures.loop_axial_track(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track))
        else:
            dgs.append(dg("axial_attitude", measures.loop_axial_attitude(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.track))
        if g.point.is_parallel(tp.vel[-1], g.PX()) and not isCircle:
            dgs.append(dg("radial_track", measures.loop_radial_track(), sms.lowpass(cutoff=2, order=5), sels.last(), IAC.intra.end_track))
        else:
            dgs.append(dg("radial_attitude", measures.loop_radial_attitude(), sms.lowpass(cutoff=2, order=5), sels.last(), IAC.intra.end_track))
        if el.roll == 0:
            dgs.append(dg("roll_angle", measures.roll_angle_p(), sms.lowpass(cutoff=1, order=5), None, IAC.intra.roll))
        else:
            dgs.append(dg("roll_angle", measures.roll_angle_p(), None, sels.last(), IAC.intra.roll))
    elif el.__class__ is StallTurn:
        dgs.append(dg("width", measures.stallturn_width(), None, None, IAC.intra.stallturn_width))
        dgs.append(dg("speed", measures.vertical_speed(), None, sels.first_and_last(), IAC.intra.stallturn_speed))
        dgs.append(dg("roll_angle", measures.roll_angle_z(), None, None, IAC.intra.roll))
        dgs.append(dg("end_yaw", measures.yaw_attitude(), None, sels.last(), IAC.intra.end_track))
    elif el.__class__ is Spin:
        dgs.append(dg("turns", measures.roll_angle_y(), None, sels.last(), IAC.intra.end_roll))
        dgs.append(dg("alpha", measures.spin_alpha_iac(), None, sels.before_recovery(rot=np.pi/4), IAC.intra.pos_autorotation_alpha))
        dgs.append(dg("drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), IAC.intra.drop_pitch_rate ))
        dgs.append(dg("peak_drop_pitch_rate", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), IAC.intra.peak_drop_pitch_rate ))
        dgs.append(dg("exit_y_track", measures.loop_radial_track(), None, sels.last(), IAC.intra.end_track))
        dgs.append(dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), IAC.intra.recovery_roll_rate ))
    elif el.__class__ is Snap:
        dgs.append(dg("turns", measures.roll_angle_y(), None, sels.last(), IAC.intra.end_roll))
        dgs.append(dg("recovery_rate_delta", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), IAC.intra.recovery_roll_rate ))
        dgs.append(dg("alpha", measures.alpha_iac(), None, sels.autorotation(brot=np.pi/4, rrot=np.pi/2), IAC.intra.autorotation_alpha))
        if last_kind is not Snap:
            dgs.append(dg("peak_break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), IAC.intra.peak_break_pitch_rate ))
            dgs.append(dg("break_pitch_rate", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), IAC.intra.break_pitch_rate ))
    if (el.__class__ is Line or el.__class__ is Loop ):
        if el.roll > 0:
            dgs.append(dg("roll_rate", measures.roll_rate(), sms.rollrate_lowpass(order=5), None, IAC.intra.rollrate))
            dgs.append(dg("roll_smoothness", measures.abs_roll_rate(), sms.lowpass(cutoff=2, order=5), None, IAC.intra.rollsmoothness))
        

    return DownGrades(dgs)
