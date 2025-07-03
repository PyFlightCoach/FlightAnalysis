import numpy as np
import geometry as g
from flightdata import State
from flightanalysis import Spin, Line, Loop, Manoeuvre, Elements


ist = State.from_transform(g.Transformation(g.Euler(np.pi, 0, 0 )))

rate = 1.7 * np.pi
nd_turns = np.pi/4
recovery_turns=np.pi
pitch=np.radians(30)
turns1 = 2 * 2 * np.pi 
turns2 = -2 * 2 * np.pi

m = Manoeuvre(Elements([
    Line("entry_line", 30, 50),
    Spin("spin1", 10, Spin.get_height(10, rate, turns1, nd_turns, 0 ), turns1, pitch, nd_turns, 0),
    Spin("spin2", 10, Spin.get_height(10, rate, turns2, 0, recovery_turns ), turns2, pitch, 0, recovery_turns),
    Line("e2", 30, 100 ),
    Loop("e3", 30, np.pi/2, 55, 0, 0)
]), Line("exit_line", 30, 50))

tp = m.create_template(ist)
State.stack(tp, "element").plot().show()