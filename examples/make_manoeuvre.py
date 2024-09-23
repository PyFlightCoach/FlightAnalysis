from flightplotting import plotsec, plot_regions
from flightplotting.traces import axis_rate_trace
from flightanalysis import (
    ManDef, BoxLocation, Position, Height, Direction, 
    Orientation, ManInfo, Heading)
import numpy as np
from flightanalysis.builders.manbuilder import r, MBTags, c45, centred
from flightanalysis.builders.f3a.manbuilder import f3amb
from flightdata import NumpyEncoder
import plotly.graph_objects as go
from json import dumps
import geometry as g

mdef: ManDef = f3amb.create(ManInfo(
    "half square", "hSqL", k=2, position=Position.END, 
    start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
    end=BoxLocation(Height.BTM)
),[
    f3amb.loop(np.pi/2),
    f3amb.roll(r(1)),
    f3amb.loop(np.pi/2), 
])

data = mdef.to_dict()
print(dumps(data, indent=2, cls=NumpyEncoder))
mdef = ManDef.from_dict(data)

it = mdef.guess_itrans(170, Heading.RIGHT)

mdef.fit_box(it)

man = mdef.create()

tp = man.create_template(it)

fig = plot_regions(tp, 'element', span=5)
fig = plotsec(tp, fig=fig, nmodels=10, scale=5)
#fig.add_traces(boxtrace())
fig.show()

#fig = go.Figure(data=axis_rate_trace(tp))
#fig.show()