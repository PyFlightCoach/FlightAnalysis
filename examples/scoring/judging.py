from json import load
from flightdata import State, Origin
from flightanalysis import SchedDef, ScheduleAnalysis, ManoeuvreAnalysis
from flightdata import Flight
import numpy as np
import pandas as pd
from flightplotting import plotsec, plotdtw
from time import time

with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)

flight = Flight.from_fc_json(data).remove_time_flutter()
box = Origin.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])
sdef = SchedDef.load(data["parameters"]["schedule"][1])



analysis = ScheduleAnalysis()
dgs = []

for mdef in sdef:
    t0 = time()
    print(f'Analyzing {mdef.info.name}')
    ma = ManoeuvreAnalysis.build(mdef, state.get_manoeuvre(mdef.info.short_name))
    scores = ma.scores()
    print( time()-t0,mdef.info.name, scores.score(), scores.summary())
    
    ma.plot_3d().show()
    
    print('Optimising Alignment')
    t0 = time()
    ma=ma.optimise_alignment()
    
    
    scores = ma.scores()
    print( time()-t0,mdef.info.name, scores.score(), scores.summary())
    ma.plot_3d().show()
    
    dgs.append(scores.summary())
    
    

df = pd.DataFrame.from_dict(dgs)
print(df)
pass



