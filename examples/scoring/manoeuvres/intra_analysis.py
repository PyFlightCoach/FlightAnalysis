from flightanalysis import ManoeuvreAnalysis as MA
from flightanalysis.manoeuvre_analysis import ElementAnalysis as EA
from json import load, dumps
import numpy as np

with open('examples/scoring/manoeuvres/mans/M.json', 'r') as f:
    ma = MA.from_dict(load(f))

from flightplotting import plotsec
from flightplotting.traces import vectors
from flightanalysis.scoring import Result, DownGrade

ea = ma.e_2

dg: DownGrade = ea.el.intra_scoring.width
res: Result = dg(ea.fl, ea.tp)

res.plot().show()

fig = ea.plot_3d()

fig.add_traces(vectors(10, ea.fl, -res.measurement.direction * np.degrees(res.sample)))
fig.show()
pass