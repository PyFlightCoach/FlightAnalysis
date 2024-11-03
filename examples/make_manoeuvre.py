from flightplotting import plotsec, plot_regions
from flightplotting.traces import axis_rate_trace
from flightanalysis import (
    ManDef, BoxLocation, Position, Height, Direction, 
    Orientation, ManInfo, Heading, ManParm, Combination, enable_logging)
import numpy as np
from flightanalysis.builders.manbuilder import r, MBTags, c45, centred
from flightanalysis.builders.f3a.manbuilder import f3amb
from flightanalysis.builders.IAC.manbuilder import iacmb    
from flightanalysis.builders.schedules.f3a_p25 import p25_def as sdef
from flightdata import NumpyEncoder
import plotly.graph_objects as go
from json import dumps
import geometry as g


enable_logging('DEBUG')

mdef: ManDef = sdef[1]

if False:
    data = mdef.to_dict()
    mdef = ManDef.from_dict(data)

it = mdef.guess_itrans(170, Heading.LTOR)

mdef.fit_box(it)

man = mdef.create()

tp = man.create_template(it)

fig = plot_regions(tp, 'element', span=5)
fig = plotsec(tp, fig=fig, nmodels=10, scale=10)
fig.add_traces(mdef.box.plot())
fig.show()

