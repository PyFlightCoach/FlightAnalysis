from flightanalysis import Loop, Line, Snap, Elements, Manoeuvre
import numpy as np
from flightdata import State
import geometry as g
from plotting import plotsec


man = Manoeuvre(Elements([
    Line('entry_line', 30, 60, 0),
    Loop('loop', 30, np.pi, 50, 0, 0),
    Snap('snap', 30, 60, 1.5*2*np.pi, np.radians(20), np.radians(45), np.radians(45)),
]), Line('exit_line', 30, 60, 0))


tp = man.create_template(State.from_transform(g.Transformation()))
plotsec(tp, nmodels=10).show()  
