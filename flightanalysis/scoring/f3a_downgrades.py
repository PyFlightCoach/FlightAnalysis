from flightanalysis.scoring.measurement import Measurement
from flightanalysis.scoring.downgrade import DownGrades, dg
from .selectors import selectors as sels
from .smoothing import smoothers as sms
from flightanalysis.scoring.criteria.f3a_criteria import F3A
import geometry as g
import numpy as np

dgs = DownGrades([
    dg("end_track_y", "track_y", Measurement.track_y, sms.lowpass(cutoff=2, order=5), sels.last(), F3A.single.track),
    dg("end_track_z", "track_z", Measurement.track_z, sms.lowpass(cutoff=2, order=5), sels.last(), F3A.single.track),
    dg("end_roll_angle", "roll", Measurement.roll_angle, sms.lowpass(cutoff=1, order=5), sels.last(), F3A.single.roll),
    dg("speed", "speed", Measurement.speed, sms.lowpass(cutoff=0.25, order=5), None, F3A.intra.speed),
    dg("line_track_y", "track_y", Measurement.track_y, sms.lowpass(cutoff=2, order=5), None, F3A.intra.track),
    dg("line_track_z", "track_z", Measurement.track_z, sms.lowpass(cutoff=2, order=5), None, F3A.intra.track),
    dg("line_roll_angle", "roll", Measurement.roll_angle, sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll),
    dg("roll_rate", "roll_rate", Measurement.roll_rate, [sms.lowpass(cutoff=2, order=5), sms.soft_ends(width=5)], None, F3A.intra.roll_rate),
    dg("loop_curvature", "curvature", Measurement.curvature_proj, [sms.lowpass(cutoff=0.5, order=5), sms.soft_ends(width=10)], None, F3A.intra.radius),
    dg("loop_track_y", "track_y", Measurement.track_proj_vel, sms.lowpass(cutoff=2, order=5), None, F3A.intra.track),
    dg("loop_track_z", "track_z", Measurement.track_proj_ang, sms.lowpass(cutoff=2, order=5), sels.last(), F3A.single.track),
    dg("loop_roll_angle", "roll", Measurement.roll_angle_p, sms.lowpass(cutoff=1, order=5), None, F3A.intra.roll),
    dg("rolling_loop_roll_angle", "roll", Measurement.roll_angle_p, sms.lowpass(cutoff=2, order=5), sels.last(), F3A.intra.roll),
    dg("stallturn_width", "width", Measurement.stallturn_width, None, None, F3A.intra.stallturn_width),
    dg("stallturn_speed", "speed", lambda fl, tp: Measurement.speed(fl, tp, g.PZ()), None, None, F3A.intra.stallturn_speed),
    dg("stallturn_roll_angle", "roll", Measurement.roll_angle_z, None, sels.last(), F3A.intra.roll),
    dg("autorotation_break_angle", "break_angle", Measurement.break_angle, None, sels.autorotation(brot=np.pi/4,rrot=np.pi/2), F3A.intra.break_angle),
    dg("autorotation_rate", "roll_rate", Measurement.autorotation_rate, sms.lowpass(cutoff=1, order=5), sels.autorotation(brot=np.pi/4,rrot=np.pi/2), F3A.intra.autorotation_rate),
    dg("autorotation_roll_angle", "roll", Measurement.roll_angle_y, None, sels.last(), F3A.single.roll),
    dg("break_alpha_delta", "dalpha", Measurement.delta_alpha, None, sels.autorot_break(rot=np.pi/4), F3A.intra.break_alpha_delta ),
    dg("recovery_alpha_delta", "dalpha", Measurement.delta_alpha, None, sels.autorot_recovery(rot=np.pi/2), F3A.intra.recovery_alpha_delta ),
    dg("track_y_decel", "track_y", Measurement.track_y, sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=5), F3A.intra.track),
    dg("track_z_decel", "track_z", Measurement.track_z, sms.lowpass(cutoff=4, order=5), sels.before_slowdown(sp=5), F3A.intra.track),
    dg("track_y_accel", "track_y", Measurement.track_y, sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=5), F3A.intra.track),
    dg("track_z_accel", "track_z", Measurement.track_z, sms.lowpass(cutoff=4, order=5), sels.after_speedup(sp=5), F3A.intra.track),
])



class DGGrps:
    exits = DownGrades([dgs.end_track_y, dgs.end_track_z, dgs.end_roll_angle])
    line = DownGrades([dgs.speed, dgs.line_track_y, dgs.line_track_z, dgs.line_roll_angle])
    roll = DownGrades([dgs.speed, dgs.line_track_y, dgs.line_track_z, dgs.roll_rate, dgs.end_roll_angle])
    loop = DownGrades([dgs.speed, dgs.loop_curvature, dgs.loop_track_y, dgs.loop_track_z, dgs.loop_roll_angle])
    rolling_loop = DownGrades([dgs.speed, dgs.loop_curvature, dgs.loop_track_y, dgs.loop_track_z, dgs.roll_rate, dgs.end_roll_angle])
    snap = DownGrades([dgs.autorotation_roll_angle])
    spin = DownGrades([dgs.autorotation_roll_angle])
    nose_drop = DownGrades([dgs.break_alpha_delta])
    pitch_break = DownGrades([dgs.break_alpha_delta])
    recovery = DownGrades([dgs.recovery_alpha_delta])
    stallturn = DownGrades([dgs.stallturn_width, dgs.stallturn_speed, dgs.stallturn_roll_angle])
    autorotation = DownGrades([dgs.autorotation_rate, dgs.autorotation_break_angle])
    st_line_decel = DownGrades([dgs.track_y_decel, dgs.track_z_decel, dgs.line_roll_angle])
    st_line_accel = DownGrades([dgs.track_y_accel, dgs.track_z_accel, dgs.line_roll_angle])
    sp_line_decel = DownGrades([dgs.track_y_decel, dgs.line_track_z, dgs.line_roll_angle])
    sp_line_accel = DownGrades([dgs.track_y_accel, dgs.track_z_accel, dgs.line_roll_angle])
    

    