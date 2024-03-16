from flightanalysis import ManoeuvreAnalysis as MA, ElementAnalysis as EA
from json import load, dump

with open('examples/scoring/manoeuvres/mans/tHat_opt.json', 'r') as f:
    ma = MA.from_dict(load(f))

from flightplotting.traces import vectors
from flightanalysis.scoring import Result, DownGrade

ea = ma[0]

#dump(ea.to_dict(), open('tests/test_schedule/test_element/loop_analysis.json', 'w'))

dg: DownGrade = ea.el.intra_scoring.roll_angle
res: Result = dg(ea.fl, ea.tp)


fig = ea.plot_3d()

fig.add_traces(vectors(5, ea.tp, 5*res.measurement.direction, name='vel_err', line=dict(color='red', width=3)))
fig.add_traces(vectors(5, ea.tp, 0.5*ea.tp.att.transform_point(ea.tp.vel), name='template_vel', line=dict(color='blue', width=3)))
fig.add_traces(vectors(5, ea.tp, 0.5*ea.fl.att.transform_point(ea.fl.vel), name='flown_vel', line=dict(color='green', width=3)))
fig.show()
res.plot().show()
pass