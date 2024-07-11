from __future__ import annotations
from typing import Self, Union
from json import load, dump
from flightdata import Flight, State, Origin, Collection, NumpyEncoder
from flightanalysis.definition import SchedDef, ScheduleInfo
from flightanalysis import __version__
from . import manoeuvre_analysis as analysis
from loguru import logger
from joblib import Parallel, delayed
import os
import pandas as pd

class ScheduleAnalysis(Collection):
    VType=analysis.Analysis
    uid='name'
    
    def __init__(self, data: list[analysis.Analysis], sinfo: ScheduleInfo):
        super().__init__(data)
        self.sinfo = sinfo

    @staticmethod
    def from_fcj(file: Union[str | bytes, dict], info: ScheduleInfo=None, proceed=True) -> ScheduleAnalysis:
        data = file if isinstance(file, dict) else load(open(file, 'r'))

        flight = Flight.from_fc_json(data)
        
        if info is None:
            info = ScheduleInfo.from_str(data["parameters"]["schedule"][1])
        
        sdef = SchedDef.load(info)
        box = Origin.from_fcjson_parameters(data["parameters"])
        state = State.from_flight(flight, box).splitter_labels(data["mans"],sdef.uids)
        direction = -state.get_manoeuvre(1)[0].direction()[0]

        if 'fcs_scores' in data and len(data['fcs_scores']) > 0:
            versions = [res['fa_version'] for res in data['fcs_scores']]
            ilatest = versions.index(max(versions))

        mas = []
        for i, mdef in enumerate(sdef):
            st = state.get_manoeuvre(mdef.uid)

            if 'fcs_scores' in data and len(data['fcs_scores']) > 0:
                df = pd.DataFrame(data['fcs_scores'][ilatest]['manresults'][i+1]['els'])
                st = st.splitter_labels(df.to_dict('records'), target_col='element')
            
            nma = analysis.Basic(i, mdef, st, direction)
            if proceed:
                nma = nma.proceed()
            mas.append(nma)

        return ScheduleAnalysis(mas,info)
    
    def append_scores_to_fcj(self, file: Union[str, dict], ofile: str=None) -> dict:
        data = file if isinstance(file, dict) else load(open(file, 'r'))

        new_results = dict(
            fa_version = __version__,
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

        if ofile:
            dump(data, open(file if ofile=='same' else ofile, 'w'), cls=NumpyEncoder, indent=2)

        return data
    
    def run_all(self) -> Self:
        def parse_analyse_serialise(pad):
            try:
                pad = analysis.parse_dict(pad)
                pad = pad.run_all()
                logger.info(f'Completed {pad.name}')
            except Exception as e:
                logger.error(f'Failed to process {pad.name}: {repr(e)}')
            return pad.to_dict()
        
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

    