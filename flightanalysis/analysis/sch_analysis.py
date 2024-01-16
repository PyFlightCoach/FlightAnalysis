from typing import Self
from json import load
from flightdata import Flight, State, Origin, Collection
from flightanalysis.definition import SchedDef, ScheduleInfo
from .man_analysis import ManoeuvreAnalysis


class ScheduleAnalysis(Collection):
    VType=ManoeuvreAnalysis

    @staticmethod
    def from_fcj(file: str) -> Self:
        with open(file, 'r') as f:
            data = load(f)

        flight = Flight.from_fc_json(data)
        box = Origin.from_fcjson_parmameters(data["parameters"])

        sdef = SchedDef.load(data["parameters"]["schedule"][1])

        state = State.from_flight(flight, box).splitter_labels(
            data["mans"],
            [m.info.short_name for m in sdef]
        )
        mas=[]
        for mdef in sdef:
            mas.append(ManoeuvreAnalysis.build(
                mdef, 
                state.get_manoeuvre(mdef.info.short_name)
            ))
        
        return ScheduleAnalysis(mas)

    @staticmethod
    def from_fcscore(file: str) -> Self:
        with open(file, 'r') as f:
            data = load(f)
        
        sdef = SchedDef.load(ScheduleInfo(**data['sinfo']))

        mas = []
        for mdef in sdef:
            mas.append(ManoeuvreAnalysis.from_fcs_dict(
                data['data'][mdef.info.short_name],
                mdef
            ))

        return ScheduleAnalysis(mas)