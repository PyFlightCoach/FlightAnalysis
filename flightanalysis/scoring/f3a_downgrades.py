from flightanalysis.scoring import Measurement, DownGrade, DownGrades
from flightanalysis.scoring.criteria.f3a_criteria import F3A
import geometry as g


dgs = DownGrades([
    DownGrade("track_y", Measurement.track_y, F3A.intra.track, "track_y"),
    DownGrade("track_z", Measurement.track_z, F3A.intra.track, "track_z"),
    DownGrade("soft_track_z", Measurement.soft_track_z, F3A.intra.track, "track_z"),
    DownGrade("soft_track_y", Measurement.soft_track_y, F3A.intra.track, "track_z"),
    DownGrade("end_track_y", Measurement.track_y, F3A.single.track, "track_y"),
    DownGrade("end_track_z", Measurement.track_z, F3A.single.track, "track_z"),
    DownGrade("end_roll_angle", Measurement.roll_angle, F3A.single.roll, "roll_angle"),
    DownGrade("roll_angle", Measurement.roll_angle, F3A.intra.roll, "roll_angle"),
    DownGrade("speed", Measurement.speed, F3A.intra.speed, "speed"),
    DownGrade("roll_rate", Measurement.roll_rate, F3A.intra.roll_rate, "roll_rate"),
    DownGrade("curvature", Measurement.curvature_proj, F3A.intra.radius, "curvature"),
    DownGrade("track_proj_vel", Measurement.track_proj_vel, F3A.intra.track, "track_y"),
    DownGrade("track_proj_ang", Measurement.track_proj_ang, F3A.single.track, "track_z"),
    DownGrade("roll_angle_p", Measurement.roll_angle_p, F3A.intra.roll, "roll_angle"),
    DownGrade("end_roll_angle_p", Measurement.roll_angle_p, F3A.single.roll, "roll_angle"),
    DownGrade("nose_drop_length", lambda fl, tp: Measurement.length(fl, tp, g.PX()), F3A.intra.spin_entry_length, "length"),
    DownGrade("nose_drop_roll_angle", lambda fl, tp: Measurement.roll_angle_proj(fl, tp, g.PY()), F3A.intra.roll, "roll_angle"),
    DownGrade("nose_drop_angle", Measurement.nose_drop, F3A.intra.nose_drop_amount, "drop_angle"),
    DownGrade("pitch_break_length", lambda fl, tp: Measurement.length(fl, tp, g.PX()), F3A.intra.pitch_break_length, "length"),
    DownGrade("recovery_length", lambda fl, tp: Measurement.length(fl, tp, g.PX()), F3A.intra.recovery_length, "length"),
    DownGrade("stallturn_width", lambda fl, tp: Measurement.length(fl, tp, g.PY()), F3A.intra.stallturn_width, "width"),
    DownGrade("stallturn_speed", lambda fl, tp: Measurement.speed(fl, tp, g.PZ()), F3A.intra.stallturn_speed, "speed"),
    DownGrade("stallturn_roll_angle", Measurement.roll_angle_z, F3A.intra.roll, "roll_angle"),
    DownGrade("autorotation_roll_angle", lambda fl, tp: Measurement.roll_angle_proj(fl, tp, g.PY()), F3A.single.roll, "roll_angle")
])


class DGGrps:
    exits = DownGrades([dgs.end_track_y, dgs.end_track_z, dgs.end_roll_angle])
    line = DownGrades([dgs.speed, dgs.track_y, dgs.track_z, dgs.roll_angle])
    roll = DownGrades([dgs.speed, dgs.track_y, dgs.track_z, dgs.roll_rate, dgs.end_roll_angle])
    loop = DownGrades([dgs.speed, dgs.curvature, dgs.track_proj_vel, dgs.track_proj_ang, dgs.roll_angle_p])
    rolling_loop = DownGrades([dgs.speed, dgs.curvature, dgs.track_proj_vel, dgs.track_proj_ang, dgs.roll_rate, dgs.end_roll_angle_p])
    nose_drop = DownGrades([dgs.nose_drop_length, dgs.nose_drop_roll_angle, dgs.nose_drop_angle])
    pitch_break = DownGrades([dgs.pitch_break_length])
    recovery = DownGrades([dgs.end_track_y, dgs.end_track_z, dgs.recovery_length, dgs.end_roll_angle])
    stallturn = DownGrades([dgs.stallturn_width, dgs.stallturn_speed, dgs.stallturn_roll_angle])
    autorotation = DownGrades([dgs.autorotation_roll_angle])
    st_line_decel = DownGrades([dgs.track_y, dgs.soft_track_z, dgs.roll_angle])
    st_line_accel = DownGrades([dgs.track_y, dgs.soft_track_z, dgs.roll_angle])
    sp_line_decel = DownGrades([dgs.soft_track_y, dgs.track_z, dgs.roll_angle])
    sp_line_accel = DownGrades([dgs.soft_track_y, dgs.soft_track_z, dgs.roll_angle])