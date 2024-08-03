from flightanalysis.scoring import Measurement, DownGrade, DownGrades
from flightanalysis.scoring.f3a_subsetters import subs
from flightanalysis.scoring.criteria.f3a_criteria import F3A
import geometry as g
import numpy as np

dgs = DownGrades([
    DownGrade("track_y", Measurement.track_y, F3A.intra.track, "track_y"),
    DownGrade("track_z", Measurement.track_z, F3A.intra.track, "track_z"),
    DownGrade("track_y_decel", Measurement.track_y, F3A.intra.track, "track_z", subs.before_slowdown(5)),
    DownGrade("track_y_accel", Measurement.track_y, F3A.intra.track, "track_z", subs.after_speedup(5)),
    DownGrade("track_z_decel", Measurement.track_z, F3A.intra.track, "track_y", subs.before_slowdown(5)),
    DownGrade("track_z_accel", Measurement.track_z, F3A.intra.track, "track_y", subs.after_speedup(5)),
    DownGrade("end_track_y", Measurement.track_y, F3A.single.track, "track_y", subs.last()),
    DownGrade("end_track_z", Measurement.track_z, F3A.single.track, "track_z", subs.last()),
    DownGrade("end_roll_angle", Measurement.roll_angle, F3A.single.roll, "roll_angle", subs.last()),
    DownGrade("roll_angle", Measurement.roll_angle, F3A.intra.roll, "roll_angle"),
    DownGrade("speed", Measurement.speed, F3A.intra.speed, "speed"),
    DownGrade("roll_rate", Measurement.roll_rate, F3A.intra.roll_rate, "roll_rate"),
    DownGrade("autorotation_rate", Measurement.autorotation_rate, F3A.intra.autorotation_rate, "roll_rate", subs.autorotation(np.pi/4, np.pi/2)),
    DownGrade("curvature", Measurement.curvature_proj, F3A.intra.radius, "curvature"),
    DownGrade("track_proj_vel", Measurement.track_proj_vel, F3A.intra.track, "track_y"),
    DownGrade("track_proj_ang", Measurement.track_proj_ang, F3A.single.track, "track_z"),
    DownGrade("roll_angle_p", Measurement.roll_angle_p, F3A.intra.roll, "roll_angle"),
    DownGrade("end_roll_angle_p", Measurement.roll_angle_p, F3A.single.roll, "roll_angle", subs.last()),
    DownGrade("stallturn_width", lambda fl, tp: Measurement.length(fl, tp, g.PY()), F3A.intra.stallturn_width, "width"),
    DownGrade("stallturn_speed", lambda fl, tp: Measurement.speed(fl, tp, g.PZ()), F3A.intra.stallturn_speed, "speed"),
    DownGrade("stallturn_roll_angle", Measurement.roll_angle_z, F3A.intra.roll, "roll_angle"),
    DownGrade("autorotation_roll_angle", lambda fl, tp: Measurement.roll_angle_proj(fl, tp, g.PY()), F3A.single.roll, "roll_angle", subs.last()),
    DownGrade("autorotation_break_angle", Measurement.break_angle, F3A.intra.break_angle, "break_angle", subs.autorotation(np.pi/4, np.pi/2)),
])


class DGGrps:
    exits = DownGrades([dgs.end_track_y, dgs.end_track_z, dgs.end_roll_angle])
    line = DownGrades([dgs.speed, dgs.track_y, dgs.track_z, dgs.roll_angle])
    roll = DownGrades([dgs.speed, dgs.track_y, dgs.track_z, dgs.roll_rate, dgs.end_roll_angle])
    loop = DownGrades([dgs.speed, dgs.curvature, dgs.track_proj_vel, dgs.track_proj_ang, dgs.roll_angle_p])
    rolling_loop = DownGrades([dgs.speed, dgs.curvature, dgs.track_proj_vel, dgs.track_proj_ang, dgs.roll_rate, dgs.end_roll_angle_p])
    nose_drop = DownGrades([])
    pitch_break = DownGrades([])
    recovery = DownGrades([])
    stallturn = DownGrades([dgs.stallturn_width, dgs.stallturn_speed, dgs.stallturn_roll_angle])
    autorotation = DownGrades([dgs.autorotation_rate, dgs.autorotation_break_angle])
    st_line_decel = DownGrades([dgs.track_y_decel, dgs.track_z_decel, dgs.roll_angle])
    st_line_accel = DownGrades([dgs.track_y_accel, dgs.track_z_accel, dgs.roll_angle])
    sp_line_decel = DownGrades([dgs.track_y_decel, dgs.track_z, dgs.roll_angle])
    sp_line_accel = DownGrades([dgs.track_y_accel, dgs.track_z_accel, dgs.roll_angle])
    snap = DownGrades([dgs.autorotation_roll_angle])
    spin = DownGrades([dgs.autorotation_roll_angle])

    