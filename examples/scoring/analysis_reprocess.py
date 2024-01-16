from flightanalysis import ScheduleAnalysis, DownGrade, Result

sa = ScheduleAnalysis.from_fcscore("examples/scoring/manual_F3A_F25_24_01_05_00000177_analysis.json")

ma=sa[-1]
ea=ma.e_5_0_break

dg: DownGrade = ea.el.intra_scoring.length
res: Result = dg(ea.fl, ea.tp)


pass