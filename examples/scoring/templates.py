from flightdata import *
from flightanalysis import *
from json import load
from flightplotting import plotsec
import geometry as g



with open("examples/data/manual_F3A_P23_23_08_11_00000094.json", "r") as f:
    data = load(f)

fl = Flight.from_fc_json(data).butter_filter(3,5)
box = Origin.from_fcjson_parmameters(data["parameters"])
flown = State.from_flight(fl, box).splitter_labels(data["mans"]).get_manoeuvre(1)


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


sdef = ScheduleInfo('f3a', 'p23').definition()
mdef=sdef.tHat

itrans = ManoeuvreAnalysis.initial_transform(mdef, flown)

man, template = ManoeuvreAnalysis.template(mdef, itrans)


fig = plotsec(template, nmodels=10).show()
#fig = plotsec(flown, nmodels=10).show()

from flightplotting.traces import axis_rate_traces


import plotly.graph_objects as go

go.Figure(
    data=axis_rate_traces(dict(flown=flown,template=template)),
    layout=dict(title='Before Alignment')
).show()

dist, aligned = ManoeuvreAnalysis.alignment(template, man, flown)
intended, int_tp = ManoeuvreAnalysis.intention(man, aligned, template)


go.Figure(
    data=axis_rate_traces(dict(flown=aligned,template=int_tp)),
    layout=dict(title='After Alignment')
).show()

corr = ManoeuvreAnalysis.correction(mdef, intended, int_tp, aligned)
corr_tp = corr.create_template(itrans, aligned)


intended= intended.copy_directions(corr)
int_tp = intended.el_matched_tp(int_tp[0], aligned)

go.Figure(
    data=axis_rate_traces(dict(flown=aligned,template=int_tp)),
    layout=dict(title='After Alignment')
).show()
fig = plotsec(int_tp, nmodels=10).show()

ma = ManoeuvreAnalysis(mdef, aligned, intended, int_tp, corr, corr_tp)

print(ma.scores().score())
pass