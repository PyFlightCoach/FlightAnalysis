from flightanalysis.builders.f3a.box import box
from flightanalysis.builders.IAC.box import unlimited_box
import plotly.graph_objects as go
from flightplotting import create_3d_plot, pointtrace, plot_regions
from flightanalysis.builders.schedules.iac_advanced2024 import sdef
from flightanalysis import Heading
import numpy as np
import geometry as g

bo = box

sched = sdef.create()
tp = sched.create_template(
    g.Transformation(sdef[0].box.middle(), sdef[0].initial_rotation(Heading.OUTTOIN))
)

fig = plot_regions(tp, "manoeuvre")
fig.add_traces(sdef[0].box.plot())
fig.show()