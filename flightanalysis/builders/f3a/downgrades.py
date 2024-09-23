from flightanalysis.scoring.measurements import measures
from flightanalysis.scoring.downgrade import DownGrades, dg, DowgradeGroups
from flightanalysis.scoring.selectors import selectors as sels
from flightanalysis.scoring.smoothing import smoothers as sms
from flightanalysis.builders.f3a.criteria import F3A
import numpy as np
from dataclasses import dataclass


dgs = DownGrades([
    dg("end_track_y", "track_y", measures.track_y(), None, sels.last(), F3A.intra.end_track),
    dg("end_track_z", "track_z", measures.track_z(), None, sels.last(), F3A.intra.end_track),
    dg("end_roll_angle", "roll", measures.roll_angle(), None, sels.last(), F3A.intra.end_roll),

    dg("speed", "speed", measures.speed(), sms.lowpass(cutoff=0.5, order=5), None, F3A.intra.speed),
    dg("line_track_y", "track_y", measures.track_y(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track),
    dg("line_track_z", "track_z", measures.track_z(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track),
    dg("line_roll_angle", "roll", measures.roll_angle(), sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll),

    dg("roll_rate", "roll_rate", measures.roll_rate(), sms.rollrate_lowpass(order=5), None, F3A.intra.rollrate),
    dg("roll_smoothness", "roll_smoothness", measures.abs_roll_rate(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.rollsmoothness),

    dg("loop_roundness", "loop_roundness", measures.curvature_proj(), sms.curvature_lowpass(order=5), None, F3A.intra.loopshape),
    dg("loop_smoothness", "loop_smoothness", measures.absolute_curvature_proj(), sms.lowpass(cutoff=2, order=5), sels.borders(tb=0.25), F3A.intra.loopsmoothness),

    dg("loop_track_y", "track_y", measures.track_proj_vel(), sms.lowpass(cutoff=2, order=5), None, F3A.intra.track),
    dg("loop_track_z", "track_z", measures.track_proj_ang(), sms.lowpass(cutoff=2, order=5), sels.last(), F3A.intra.end_track),
    dg("loop_roll_angle", "roll", measures.roll_angle_p(), sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll),
    dg("rolling_loop_roll_angle", "roll", measures.roll_angle_p(), None, sels.last(), F3A.intra.roll),

    dg("stallturn_width", "width", measures.stallturn_width(), None, None, F3A.intra.stallturn_width),
    dg("stallturn_speed", "speed", measures.vertical_speed(), None, sels.first_and_last(), F3A.intra.stallturn_speed),
    dg("stallturn_roll_angle", "roll", measures.roll_angle_z(), None, None, F3A.intra.roll),

    dg("snap_spin_turns", "roll", measures.roll_angle_y(), None, sels.last(), F3A.intra.end_roll),# correct number of turns performed
    dg("spin_alpha", "alpha", measures.spin_alpha(), None, sels.before_recovery(rot=np.pi/4), F3A.intra.pos_autorotation_alpha),#alpha > 7.5 until last 45 degrees of turn
    dg("drop_pitch_rate", "pitch", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), F3A.intra.drop_pitch_rate ),#pitch down rate > 0.3 until 15 degree of turn
    dg("peak_drop_pitch_rate", "peak_pitch", measures.pitch_down_rate(), None, sels.autorot_break(rot=np.radians(15)), F3A.intra.peak_drop_pitch_rate ),#pitch down rate > 0.3 until 15 degree of turn
    dg("spin_track_y", "track_y", measures.track_proj_vel(), None, sels.last(), F3A.intra.end_track),

    dg("recovery_rate_delta", "recovery", measures.delta_p(), None, sels.autorot_recovery(rot=np.pi/24), F3A.intra.recovery_roll_rate ),#roll rate reducing in last 45 degrees of turn

    dg("break_pitch_rate", "break", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), F3A.intra.break_pitch_rate ),
    dg("peak_break_pitch_rate", "peak_break", measures.pitch_rate(), None, sels.autorot_break(rot=np.pi/4), F3A.intra.peak_break_pitch_rate ),
    dg("snap_alpha", "alpha", measures.alpha(), None, sels.autorotation(brot=np.pi/4, rrot=np.pi/2), F3A.intra.autorotation_alpha),#alpha > 7.5

    dg("track_y_before_slowdown", "track_y", measures.track_y(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.track),
    dg("track_z_before_slowdown", "track_z", measures.track_z(), sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=13), F3A.intra.track),
    dg("pitch_after_slowdown", "pitch", measures.pitch_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track),
    dg("yaw_after_slowdown", "yaw", measures.yaw_attitude(), None, sels.after_slowdown(sp=13), F3A.intra.track),

    dg("track_y_after_speedup", "track_y", measures.track_y(), sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=13), F3A.intra.track),
    dg("track_z_after_speedup", "track_z", measures.track_z(), sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=13), F3A.intra.track),
    dg("initial_track_y_after_speedup", "itrack_y", measures.track_y(), sms.lowpass(cutoff=4, order=5), [sels.after_speedup(sp=13), sels.first()], F3A.intra.end_track),
    dg("initial_track_z_after_speedup", "itrack_z", measures.track_z(), sms.lowpass(cutoff=4, order=5), [sels.after_speedup(sp=13), sels.first()], F3A.intra.end_track),

    dg("pitch_before_speedup", "pitch", measures.pitch_attitude(), None, sels.first(), F3A.intra.end_track),

    dg("end_yaw", "yaw", measures.yaw_attitude(), None, sels.last(), F3A.intra.end_track),
])

@dataclass
class F3ADowngradeGroups(DowgradeGroups):
    first_snap: DownGrades
    rebound_snap: DownGrades
    st_line_before: DownGrades
    st_line_after: DownGrades
    sp_line_before: DownGrades
    sp_line_after: DownGrades


dggrps = F3ADowngradeGroups(
    exits = DownGrades([dgs.end_track_y, dgs.end_track_z, dgs.end_roll_angle]),
    line = DownGrades([dgs.speed, dgs.line_track_y, dgs.line_track_z, dgs.line_roll_angle]),
    roll = DownGrades([dgs.speed, dgs.line_track_y, dgs.line_track_z, dgs.roll_rate, dgs.roll_smoothness, dgs.end_roll_angle]),
    loop = DownGrades([dgs.speed, dgs.loop_roundness, dgs.loop_smoothness, dgs.loop_track_y, dgs.loop_track_z, dgs.loop_roll_angle]),
    rolling_loop = DownGrades([dgs.speed, dgs.loop_roundness, dgs.loop_smoothness, dgs.loop_track_y, dgs.loop_track_z, dgs.roll_rate, dgs.roll_smoothness, dgs.end_roll_angle]),
    snap = DownGrades([dgs.snap_spin_turns, dgs.peak_break_pitch_rate, dgs.break_pitch_rate, dgs.snap_alpha, dgs.recovery_rate_delta, dgs.end_track_y, dgs.end_track_z]),
    spin = DownGrades([dgs.snap_spin_turns, dgs.spin_alpha, dgs.peak_drop_pitch_rate, dgs.drop_pitch_rate, dgs.recovery_rate_delta, dgs.spin_track_y, dgs.loop_track_z]),
    stallturn = DownGrades([dgs.stallturn_width, dgs.stallturn_speed, dgs.stallturn_roll_angle, dgs.end_yaw]),
    first_snap = DownGrades([dgs.snap_spin_turns, dgs.peak_break_pitch_rate, dgs.break_pitch_rate, dgs.snap_alpha, dgs.recovery_rate_delta]),
    rebound_snap = DownGrades([dgs.snap_spin_turns, dgs.snap_alpha, dgs.recovery_rate_delta, dgs.end_track_y, dgs.end_track_z]),
    st_line_before = DownGrades([dgs.track_y_before_slowdown, dgs.track_z_before_slowdown, dgs.line_roll_angle, dgs.pitch_after_slowdown, dgs.yaw_after_slowdown]),
    st_line_after = DownGrades([dgs.initial_track_y_after_speedup, dgs.initial_track_z_after_speedup, dgs.track_y_after_speedup, dgs.track_z_after_speedup, dgs.line_roll_angle])  ,
    sp_line_before = DownGrades([dgs.track_y_before_slowdown, dgs.track_z_before_slowdown, dgs.line_roll_angle, dgs.yaw_after_slowdown]),
    sp_line_after = DownGrades([dgs.line_track_y, dgs.line_track_z, dgs.line_roll_angle]),
)
#    sp_line_after_speedup = DownGrades([dgs.line_track_y, dgs.line_track_z, dgs.line_roll_angle])
    

    