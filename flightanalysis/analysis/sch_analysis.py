from __future__ import annotations
from typing import Self, Union
from json import load, dump
from flightdata import Flight, State, Origin, Collection
from flightanalysis.definition import SchedDef, ScheduleInfo
from . import manoeuvre_analysis as analysis
from loguru import logger
from joblib import Parallel, delayed
import os
import pandas as pd
from importlib.metadata import version
from packaging import version as pkgversion


class ScheduleAnalysis(Collection):
    VType=analysis.Analysis
    uid='name'
    
    def __init__(self, data: list[analysis.Analysis], sinfo: ScheduleInfo):
        super().__init__(data)
        self.sinfo = sinfo

    @staticmethod
    def from_fcj(file: Union[str, dict], info: ScheduleInfo=None) -> ScheduleAnalysis:
        data = load(open(file, 'r')) if isinstance(file, str) else file

        flight = Flight.from_fc_json(data)
        
        if info is None:
            info = ScheduleInfo.from_str(data["parameters"]["schedule"][1])
        
        sdef = SchedDef.load(info)
        box = Origin.from_fcjson_parmameters(data["parameters"])
        state = State.from_flight(flight, box).splitter_labels(data["mans"],sdef.uids)
        direction = -state.get_manoeuvre(1)[0].direction()[0]

        if 'fcs_scores' in data:
            versions = [pkgversion.parse(res['fa_version']) for res in data['fcs_scores']]
            ilatest = versions.index(max(versions))

        mas = []
        for i, mdef in enumerate(sdef):
            st = state.get_manoeuvre(mdef.uid)

            if 'fcs_scores' in data and len(data['fcs_scores']) > 0:
                df = pd.DataFrame(data['fcs_scores'][ilatest]['manresults'][i+1]['els'])
                st = st.splitter_labels(df.to_dict('records'), target_col='element')
            
            mas.append(analysis.Basic(i, mdef, st, direction).proceed())

        return ScheduleAnalysis(mas,info)
    
    def append_scores_to_fcj(self, file: Union[str, dict]) -> dict:
        data = load(open(file, 'r')) if isinstance(file, str) else file

        new_results = dict(
            fa_version = version('flightanalysis'),
            manresults = [None] + \
                [man.fcj_results() if hasattr(man, 'fcj_results') else None for man in self]
        )

        if 'fcs_scores' not in data:
            data['fcs_scores'] = []

        for res in data['fcs_scores']:
            if res['fa_version'] == new_results['fa_version']:
                res['manresults'] = new_results['manresults']
                break
        else:
            data['fcs_scores'].append(new_results)

        return data
        

    def run_all(self) -> Self:
        def parse_analyse_serialise(pad):
            res = analysis.parse_dict(pad).run_all()
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
    
    
    def scores(self):
        scores = {}
        total = 0
        scores = {ma.name: (ma.scores.score() if hasattr(ma, 'scores') else 0) for ma in self}
        total = sum([ma.mdef.info.k * v for ma, v in zip(self, scores.values())])
        return total, scores

    def summarydf(self):
        return pd.DataFrame([ma.scores.summary() if hasattr(ma, 'scores') else {} for ma in self])

    