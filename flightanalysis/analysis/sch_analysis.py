from __future__ import annotations
from typing import Self, Union
from json import load
from flightdata import Flight, State, Origin, Collection
from flightanalysis.definition import SchedDef, ScheduleInfo
from . import manoeuvre_analysis as analysis
from loguru import logger
from joblib import Parallel, delayed
import os
import pandas as pd
from importlib.metadata import version
import geometry as g


class ScheduleAnalysis(Collection):
    VType=analysis.Analysis
    uid='name'
    
    def __init__(self, data: list[analysis.Analysis], sinfo: ScheduleInfo):
        super().__init__(data)
        self.sinfo = sinfo

    @staticmethod
    def from_fcj(file: Union[str, dict], info: ScheduleInfo=None) -> ScheduleAnalysis:
        if isinstance(file, str):
            data = load(open(file, 'r'))
        else:
            data = file
        flight = Flight.from_fc_json(data)
        
        if info is None:
            info = ScheduleInfo.from_str(data["parameters"]["schedule"][1])
        
        sdef = SchedDef.load(info)
        box = Origin.from_fcjson_parmameters(data["parameters"])
        state = State.from_flight(flight, box).splitter_labels(
            data["mans"],
            sdef.uids
        )
        direction = -state.get_manoeuvre(1)[0].direction()[0]

        return ScheduleAnalysis(
            [analysis.Basic(
                i,
                mdef, 
                state.get_manoeuvre(mdef.uid), 
                direction
            ) for i, mdef in enumerate(sdef)],
            info
        )
    
    def run_all(self) -> Self:
        def parse_analyse_serialise(pad):
            res = analysis.Basic.from_dict(pad).run_all()
            logger.info(f'Completed {res.name}')
            return res.to_dict()
        
        logger.info(f'Starting {os.cpu_count()} analysis processes')
        madicts = Parallel(n_jobs=os.cpu_count())(
            delayed(parse_analyse_serialise)(ma.to_dict()) for ma in self
        )

        return ScheduleAnalysis([analysis.Scored.from_dict(mad) for mad in madicts], self.sinfo)  

    def optimize_alignment(self) -> Self:

        def parse_analyse_serialise(mad):
            an = analysis.Complete.from_dict(mad)
            return an.run_all().to_dict()

        logger.info(f'Starting {os.cpu_count()} alinment optimisation processes')
        inmadicts = [mdef.to_dict() for mdef in self]
        madicts = Parallel(n_jobs=os.cpu_count())(delayed(parse_analyse_serialise)(mad) for mad in inmadicts)
        return ScheduleAnalysis([analysis.Scored.from_dict(mad) for mad in madicts], self.sinfo)
    
    @staticmethod
    def from_fcscore(file: Union[str, dict], fallback=True) -> ScheduleAnalysis:
        if isinstance(file, str) or isinstance(file, os.PathLike):
            data = load(open(file, 'r'))
        else:
            data = file
        sinfo = ScheduleInfo(**data['sinfo'])
        sdef = SchedDef.load(sinfo)

        mas = []
        for mdef in sdef:
            mas.append(analysis.Scored.from_dict(
                data['data'][mdef.info.short_name],
                fallback
            ))

        return ScheduleAnalysis(mas, sinfo)
    
    def scores(self):
        scores = {}
        total = 0
        scores = {ma.name: (ma.scores.score() if hasattr(ma, 'scores') else 0) for ma in self}
        total = sum([ma.mdef.info.k * v for ma, v in zip(self, scores.values())])
        return total, scores

    def summarydf(self):
        return pd.DataFrame([ma.scores.summary() if hasattr(ma, 'scores') else {} for ma in self])

    def to_fcscore(self, name: str) -> dict:        
        total, scores = self.scores()
       
        odata = dict(
            name = name,
            client_version = 'Py',
            server_version = version('flightanalysis'),
            sinfo = self.sinfo.__dict__,
            score = total,
            manscores = scores,
            data = self.to_dict()
        )
        return odata
