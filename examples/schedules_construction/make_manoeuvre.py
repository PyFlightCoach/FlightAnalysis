from flightanalysis.schedule import *
import numpy as np
from flightanalysis import *


mdef = f3amb.create(ManInfo(
    "Top Hat", "tHat", k=4, position=Position.CENTRE, 
    start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
    end=BoxLocation(Height.BTM)
),[
    f3amb.loop(np.pi/2),
    f3amb.roll("2x4"),
    f3amb.loop(np.pi/2), 
    centred(f3amb.roll("1/2",line_length=100)),
    f3amb.loop(-np.pi/2),
    f3amb.roll("2x4"),
    f3amb.loop(-np.pi/2)
])

it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)



from flightdata import State
from flightplotting import plotdtw, boxtrace, plotsec
fig = plotdtw(tp, tp.data.element.unique())
fig = plotsec(tp, fig=fig, nmodels=20, scale=3)
#fig.add_traces(boxtrace())
fig.show()

