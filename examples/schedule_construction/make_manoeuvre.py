from flightplotting import plotsec, plot_regions
from flightplotting.traces import axis_rate_trace
from flightanalysis import (
    ManDef, BoxLocation, Position, Height, Direction, 
    Orientation, ManInfo, r, MBTags, c45, centred, ManParm, Combination)
import numpy as np
from flightanalysis.definition import f3amb
from flightdata import NumpyEncoder
import plotly.graph_objects as go
from json import dumps

mdef: ManDef = f3amb.create(ManInfo(
            "Figure S", "figS", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(r(3/8)),
            f3amb.loop(r(1/8), rolls="rke_opt[0]"),
            MBTags.CENTRE,
            f3amb.loop("rke_opt[1]", ke=np.pi/2),
            f3amb.loop("rke_opt[2]", ke=np.pi/2, rolls="rke_opt[3]"),
            MBTags.CENTRE
        ],
        rke_opt=ManParm("rke_opt", 
            Combination(desired=r([
                [1/4, 3/8, 1/8, 1/4], 
                [-1/4, -3/8, -1/8, -1/4]
        ])), 0))


data = mdef.to_dict()
print(dumps(data, indent=2, cls=NumpyEncoder))
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