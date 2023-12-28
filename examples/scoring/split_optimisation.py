'''
    Trial of running an optimiser to find the optimum split location between two
    elements. A simple manoeuvre is created(half loop and entry line). a dummy
    flown manoeuvre is also created with the split in slightly the wrong place. 
    a local minimizer is then run to find the minimum intra element downgrade, 
    which corresponds to the split moving back to the correct location.
'''

from flightdata import *
from flightanalysis import *
import geometry as g
import numpy as np
from flightplotting import plotdtw, axis_rate_traces
import plotly.graph_objects as go
import plotly.express as px

mdef = f3amb.create(ManInfo(
    "Half Loop", "hloop", k=2, position=Position.END, 
    start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
    end=BoxLocation(Height.TOP)
),[
    f3amb.loop(np.pi),
])

itrans = mdef.info.initial_transform(170, 1)
man = mdef.create(itrans)
tp = man.create_template(itrans)


man2 = man.copy()
man2.elements.e_0.radius=40
fl = man2.create_template(itrans).remove_labels()

al = fl.label(manoeuvre='hloop', element=tp.element[len(tp)-len(fl):])  # simulate a poor alignment

from scipy.optimize import minimize


def dg(shift, manoeuvre, template):
    al2 = al.shift_label_ratio(shift[0], manoeuvre='hloop', element='entry_line')
    manoeuvre, template = manoeuvre.match_intention(template[0], al2)
    intra = manoeuvre.analyse(al2, template)
    return intra.total

cost = lambda x: dg(x, man, tp)

res = minimize(cost, [0.25], bounds=[[-1.0,1.0]], method='Nelder-Mead')

al2 = al.shift_label_ratio(res.x, manoeuvre='hloop', element='entry_line')
#px.line(intra.e_0.radius.sample).show()
plotdtw(al, tp.data.element.unique()).show()
plotdtw(al2, tp.data.element.unique()).show()
pass
#go.Figure(data=axis_rate_traces(dict(tp=tp,al=al))).show()

