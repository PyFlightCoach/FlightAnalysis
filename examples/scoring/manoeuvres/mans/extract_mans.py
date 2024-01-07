from json import load, dump
from flightdata import State, Origin
from flightanalysis import SchedDef
from flightdata import Flight, NumpyEncoder

    

with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Origin.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])
sdef = SchedDef.load(data["parameters"]["schedule"][1])

from flightanalysis import ScheduleAnalysis, ManoeuvreAnalysis

analysis = ScheduleAnalysis()
dgs = []

for mdef in sdef:
    ma = ManoeuvreAnalysis.build(mdef, state.get_manoeuvre(mdef.info.short_name))
    with open(f'examples/scoring/manoeuvres/mans/{mdef.info.short_name}.json', 'w') as f:
        dump(ma.to_dict(), f, cls=NumpyEncoder)
