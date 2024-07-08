from flightplotting import plotsec, plot_regions
from flightplotting.traces import axis_rate_trace
from flightanalysis import (
    ManDef, BoxLocation, Position, Height, Direction, 
    Orientation, ManInfo, r, MBTags, c45, centred)
import numpy as np
from flightanalysis.definition import f3amb
import plotly.graph_objects as go
from json import dumps

mdef: ManDef = f3amb.create(ManInfo(
    "Figure Z", "Z", k=4, position=Position.CENTRE, 
    start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
    end=BoxLocation(Height.TOP)
),[
    f3amb.loop(3*np.pi/4),
    centred(f3amb.snap(r(1))),
    f3amb.loop(-3*np.pi/4),
], line_length=60, loop_radius=50)

data = mdef.to_dict()
print(dumps(data, indent=2))
mdef = ManDef.from_dict(data)

it = mdef.info.initial_transform(170, 1)

man = mdef.create(it)

tp = man.create_template(it)

fig = plot_regions(tp, 'element')
fig = plotsec(tp, fig=fig, nmodels=10, scale=2)
#fig.add_traces(boxtrace())
fig.show()

fig = go.Figure(data=axis_rate_trace(tp))
fig.show()