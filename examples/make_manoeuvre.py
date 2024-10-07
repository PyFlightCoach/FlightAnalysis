from flightplotting import plotsec, plot_regions
from flightplotting.traces import axis_rate_trace
from flightanalysis import (
    ManDef, BoxLocation, Position, Height, Direction, 
    Orientation, ManInfo, Heading, ManParm, Combination)
import numpy as np
from flightanalysis.builders.manbuilder import r, MBTags, c45, centred
from flightanalysis.builders.f3a.manbuilder import f3amb
from flightanalysis.builders.IAC.manbuilder import iacmb    
from flightanalysis.builders.schedules.baeapower_advanced2024 import sdef
from flightdata import NumpyEncoder
import plotly.graph_objects as go
from json import dumps
import geometry as g

mdef: ManDef = sdef[4]

data = mdef.to_dict()
print(dumps(data, indent=2, cls=NumpyEncoder))
mdef = ManDef.from_dict(data)

it = mdef.guess_itrans(600, Heading.RIGHT)

mdef.fit_box(it)

man = mdef.create()

tp = man.create_template(it)

fig = plot_regions(tp, 'element', span=5)
fig = plotsec(tp, fig=fig, nmodels=10, scale=20)

fig.show()

