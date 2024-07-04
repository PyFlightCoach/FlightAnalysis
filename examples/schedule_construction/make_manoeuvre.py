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
            "Triangle", "trgle", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi/4),
            f3amb.roll("2x4"),
            f3amb.loop(-np.pi*3/4), 
            centred(f3amb.roll(r(1),line_length=str(2 * c45 * f3amb.mps.line_length))),
            f3amb.loop(-np.pi*3/4),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/4),
            MBTags.CENTRE
        ], line_length=150)

data = mdef.to_dict()
print(dumps(data, indent=2))
mdef = ManDef.from_dict(data)
mdef.mps.line_length.defaul=300
it = mdef.info.initial_transform(170, 1)

man = mdef.create(it)

tp = man.create_template(it)

fig = plot_regions(tp, 'element')
fig = plotsec(tp, fig=fig, nmodels=10, scale=2)
#fig.add_traces(boxtrace())
fig.show()

fig = go.Figure(data=axis_rate_trace(tp))
fig.show()