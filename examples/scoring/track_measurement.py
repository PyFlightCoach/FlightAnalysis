from flightanalysis import Line, Measurement
import numpy as np
from flightdata import State
import geometry as g

line = Line(30, 100, 2*np.pi, "test" )


fl = line.create_template(
    State.from_transform(g.Transformation(g.Point(50, 150, 50), g.Euldeg(0, 178, 5)), vel=g.PX(30))
)

tp = line.create_template(
    State.from_transform(g.Transformation(g.Point(50, 150, 50), g.Euldeg(0, 180, 0)), vel=g.PX(30))
)


from flightplotting import plotsec, boxtrace

fig = plotsec([fl, tp], nmodels=10, scale=2)

fig.add_traces(boxtrace())
fig.show()


m = Measurement.track_y(fl, tp, fl[0].transform)

import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    y=m.visibility
))
fig.show()
pass