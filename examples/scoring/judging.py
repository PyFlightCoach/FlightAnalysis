from json import load
from flightdata import State, Origin
from flightanalysis import SchedDef, ScheduleAnalysis, ManoeuvreAnalysis
from flightdata import Flight
import numpy as np
import pandas as pd
from flightplotting import plotsec


with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)

flight = Flight.from_fc_json(data)
box = Origin.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])
sdef = SchedDef.load(data["parameters"]["schedule"][1])



analysis = ScheduleAnalysis()
dgs = []

for mdef in sdef:
    
    ma = ManoeuvreAnalysis.build(mdef, state.get_manoeuvre(mdef.info.short_name))
    plotsec(ma.intended_template).show()
    scores = ma.scores()

    dgs.append(scores.summary())
    print(mdef.info.short_name, scores.score(), dgs[-1])

df = pd.DataFrame.from_dict(dgs)
print(df)
pass



