from __future__ import annotations
from typing import Self, Union
from json import load, dump
from flightdata import Flight, State, Origin, Collection
from flightanalysis.definition import SchedDef, ScheduleInfo
from . import manoeuvre_analysis as analysis
from flightdata.base import NumpyEncoder
from loguru import logger
from joblib import Parallel, delayed
import os
import pandas as pd


class ScheduleAnalysis(Collection):
    VType=analysis.Analysis
    uid='name'
    
    @staticmethod
    def from_fcj(file: Union[str, dict], info: ScheduleInfo=None) -> ScheduleAnalysis:
        if isinstance(file, str):
            with open(file, 'r') as f:
                data = load(f)
        else:
            data = file
        flight = Flight.from_fc_json(data)
        box = Origin.from_fcjson_parmameters(data["parameters"])
        if info is None:
            info = ScheduleInfo.from_str(data["parameters"]["schedule"][1])
        sdef = SchedDef.load(info)

        state = State.from_flight(flight, box).splitter_labels(
            data["mans"],
            [m.info.short_name for m in sdef]
        )

        direction = -state.get_manoeuvre(0)[0].direction()[0]

        return ScheduleAnalysis(
            [analysis.Basic(
                mdef, 
                state.get_manoeuvre(mdef.info.short_name), 
                direction,
                analysis.AlinmentStage.SETUP
            ) for mdef in sdef]
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

        return ScheduleAnalysis([analysis.Scored.from_dict(mad) for mad in madicts])
    


    def optimize_alignment(self) -> Self:

        def parse_analyse_serialise(mad):
            an = analysis.Complete.from_dict(mad)
            an.stage = analysis.AlinmentStage.SECONDARY
            return an.run_all().to_dict()

        logger.info(f'Starting {os.cpu_count()} alinment optimisation processes')
        inmadicts = [mdef.to_dict() for mdef in self]
        madicts = Parallel(n_jobs=os.cpu_count())(delayed(parse_analyse_serialise)(mad) for mad in inmadicts)
        return ScheduleAnalysis([analysis.Scored.from_dict(mad) for mad in madicts])
    
    @staticmethod
    def from_fcscore(file: Union[str, dict]) -> Self:
        if isinstance(file, str) or isinstance(file, os.PathLike):
            with open(file, 'r') as f:
                data = load(f)
        else:
            data = file
                    
        sdef = SchedDef.load(ScheduleInfo(**data['sinfo']))

        mas = []
        for mdef in sdef:
            mas.append(analysis.Scored.from_dict(
                data['data'][mdef.info.short_name],
                mdef
            ))

        return ScheduleAnalysis(mas)
    
    def scores(self):
        scores = {}
        total = 0
        scores = {ma.mdef.info.short_name: ma.scores.score() for ma in self}
        total = sum([ma.mdef.info.k * v for ma, v in zip(self, scores.values())])
        return total, scores

    def summarydf(self):
        return pd.DataFrame([ma.scores.summary() if hasattr(ma, 'scores') else {} for ma in self])

    def to_fcscore(self, name: str, sinfo: ScheduleInfo) -> dict:        
        total, scores = self.scores()
       
        odata = dict(
            name = name,
            client_version = 'Py',
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