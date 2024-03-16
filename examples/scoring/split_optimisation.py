'''
    Trial of running an optimiser to find the optimum split location between two
    elements. A simple manoeuvre is created(half loop and entry line). a dummy
    flown manoeuvre is also created with the split in slightly the wrong place. 
    a local minimizer is then run to find the minimum intra element downgrade, 
    which corresponds to the split moving back to the correct location.
'''
import numpy as np
from flightanalysis import ManInfo, f3amb, BoxLocation, Height, Direction, Orientation, Position, loop
from flightplotting import plotdtw
from time import time

mdef = f3amb.create(ManInfo(
    "Half Loop", "hloop", k=2, position=Position.END, 
    start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
    end=BoxLocation(Height.TOP)
),[
    loop(np.pi),
])

itrans = mdef.info.initial_transform(170, 1)
man = mdef.create(itrans)
tp = man.create_template(itrans)


man2 = man.copy()
man2.elements.e_0.radius=40
fl = man2.create_template(itrans).remove_labels()

al = fl.label(manoeuvre='hloop', element=tp.element[len(tp)-len(fl):])  # simulate a poor alignment


els = man.all_elements()

t0=time()
al2 = man.optimise_alignment(al[0], al)
print(time() - t0)


#px.line(intra.e_0.radius.sample).show()
plotdtw(al, tp.data.element.unique()).show()
plotdtw(al2, tp.data.element.unique()).show()
pass
#go.Figure(data=axis_rate_traces(dict(tp=tp,al=al))).show()

