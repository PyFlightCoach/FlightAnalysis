from flightplotting import plotdtw, plotsec
from flightplotting.traces import axis_rate_trace
from flightanalysis import CrossDirection
import plotly.graph_objects as go

from imac_sport2024 import sdef

mdef = sdef.hB


it = mdef.info.initial_transform(220, 1, CrossDirection.OUT)
man = mdef.create(it)

tp = man.create_template(it)



fig = plotdtw(tp, tp.data.element.unique())
fig = plotsec(tp, fig=fig, nmodels=10, scale=2)
#fig.add_traces(boxtrace())
fig.show()

fig = go.Figure(data=axis_rate_trace(tp))
fig.show()