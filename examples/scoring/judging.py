from flightanalysis import ScheduleAnalysis, set_log_level, Scored


set_log_level("DEBUG")

analysis = ScheduleAnalysis.from_fcj("examples/data/manual_F3A_P23_22_05_31_00000350.json")

sa: Scored = analysis[0].run_all()

print(sa.scores.summary())
pass