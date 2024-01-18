from flightanalysis import ScheduleAnalysis, DownGrade, Result, ManoeuvreAnalysis

sa = ScheduleAnalysis.from_fcscore("examples/scoring/example_analysis_p23.json")

ma=sa.M.optimise_alignment()

ea=ma.e_2

dg: DownGrade = ea.el.intra_scoring.roll_angle
res: Result = dg(ea.fl, ea.tp)


pass