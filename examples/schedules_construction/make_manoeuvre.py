from flightanalysis.schedule import *
import numpy as np
from flightanalysis import *
from flightdata import State

if True:
    mdef = f3amb.create(ManInfo(
            "Square on Corner", "sLoop", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi/4, rolls="roll_option[0]"),
            f3amb.line(),
            f3amb.loop("roll_option[1]", rolls=r(1/2), ke=True),
            f3amb.line(),
            centred(f3amb.loop("roll_option[2]", rolls=r(1/2), ke=True)),
            f3amb.line(),
            f3amb.loop("roll_option[3]", rolls=r(1/2), ke=True),
            f3amb.line(),
            f3amb.loop("roll_option[4]", rolls="roll_option[5]", ke=True),
            MBTags.CENTRE
        ], 
        roll_option=ManParm("roll_option", Combination(desired=[
            [r(1/4), -r(1/4), r(1/4), -r(1/4), r(1/8), -r(1/4)], 
            [-r(1/4), r(1/4), -r(1/4), r(1/4), -r(1/8), r(1/4)]
        ]), 0),
        line_length=70
        )
else:
    from imac_unlimited_2024 import  sdef
    mdef = sdef[7]

#mdef.mps.top_roll_option.default = 1

it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)




from flightdata import State
from flightplotting import plotdtw, boxtrace, plotsec
from flightplotting.traces import axis_rate_trace

import plotly.graph_objects as go

fig = plotdtw(tp, tp.data.element.unique())
fig = plotsec(tp, fig=fig, nmodels=10, scale=2)
#fig.add_traces(boxtrace())
fig.show()

fig = go.Figure(data=axis_rate_trace(tp))
fig.show()