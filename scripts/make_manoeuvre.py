from flightplotting import plotdtw, plotsec
from flightplotting.traces import axis_rate_trace
from flightanalysis import ManDef, BoxLocation, Position, Height, Direction, Orientation, ManInfo, r
from flightanalysis.definition import f3amb
import plotly.graph_objects as go


mdef: ManDef = f3amb.create(ManInfo(
            "Loop", "loop", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(r(1), rolls=[r(0.5), -r(0.5)], rollangle=r(0.5), reversible=True),
        ],
        loop_radius=100,
    )


it = mdef.info.initial_transform(170, 1)
mdef.mps.e_0_rolls.defaul = 1
man = mdef.create(it)

tp = man.create_template(it)

fig = plotdtw(tp, tp.data.element.unique())
fig = plotsec(tp, fig=fig, nmodels=10, scale=2)
#fig.add_traces(boxtrace())
fig.show()

fig = go.Figure(data=axis_rate_trace(tp))
fig.show()