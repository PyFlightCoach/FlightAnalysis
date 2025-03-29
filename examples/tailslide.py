from flightanalysis import Loop, Line, Snap, Elements, Manoeuvre
import numpy as np
from flightdata import State
import geometry as g
from plotting import plotsec

from flightanalysis.elements.tail_slide import TailSlide


# man = Manoeuvre(Elements([
#    Line('entry_line', 30, 60, 0),
#    Loop('loop', 30, np.pi/2, 50, 0, 0),
#    Line("upline", 30, 100, 0),
#    TailSlide("tslide", -5, np.pi, np.radians(30), np.pi),
#    Line("downline", 30, 100, 0),
#    Loop("loop2", 30, np.pi/2, 50, 0,0 )
# ]), Line('exit_line', 30, 60, 0))
#tp = man.create_template(State.from_transform(g.Transformation()))


tp = TailSlide("tslide", -5, -np.pi, np.radians(30), np.pi).create_template(
    State.from_transform(g.Transformation(g.Euler(0, -np.pi/2, 0)))
)

plotsec(tp, nmodels=10, scale=1).show()
