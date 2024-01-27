from typing import Self, Union
from json import load, dump
from flightdata import Flight, State, Origin, Collection
from flightanalysis.definition import SchedDef, ScheduleInfo
from .man_analysis import ManoeuvreAnalysis
from flightdata.base import NumpyEncoder


class ScheduleAnalysis(Collection):
    VType=ManoeuvreAnalysis

    @staticmethod
    def from_fcj(file: Union[str, dict]) -> Self:
        if isinstance(file, str):
            with open(file, 'r') as f:
                data = load(f)
        else:
            data = file
        flight = Flight.from_fc_json(data)
        box = Origin.from_fcjson_parmameters(data["parameters"])
        info = ScheduleInfo.from_str(data["parameters"]["schedule"][1])
        sdef = SchedDef.load(info)

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
        
        sa =  ScheduleAnalysis(mas)
        
        return sa
        
    def optimize_alignment(self) -> Self:
        mas = []
        for ma in self:
            mas.append(ma.optimise_alignment())
        return ScheduleAnalysis(mas)
    
    @staticmethod
    def from_fcscore(file: Union[str, dict]) -> Self:
        if isinstance(file, str):
            with open(file, 'r') as f:
                data = load(f)
        else:
            data = file
                    
        sdef = SchedDef.load(ScheduleInfo(**data['sinfo']))

        mas = []
        for mdef in sdef:
            mas.append(ManoeuvreAnalysis.from_fcs_dict(
                data['data'][mdef.info.short_name],
                mdef
            ))

        return ScheduleAnalysis(mas)
    
    
    def to_fcscore(self, name: str, sinfo: ScheduleInfo) -> dict:        
        scores = {}
        total = 0
        for ma in self:
            scores[ma.mdef.info.short_name] = ma.scores().score()
            total += scores[ma.mdef.info.short_name] * ma.mdef.info.k

       
        odata = dict(
            name = name,
            client_version = 'None',
            server_version = '',
            sinfo = sinfo.__dict__,
            score = total,
            manscores = scores,
            data = self.to_dict(True)
        )
        return odata

    def dump_fcscore(self, name: str, sinfo: ScheduleInfo, file: str):
        with open(file, 'w') as f:
            dump(self.to_fcscore(name, sinfo), f, cls=NumpyEncoder)