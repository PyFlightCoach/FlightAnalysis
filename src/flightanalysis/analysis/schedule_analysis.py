from __future__ import annotations
from xmlrpc.client import boolean
from flightdata import State
from typing import Self
from flightdata import Collection
from flightanalysis import ManDef, SchedDef
from schemas import AJson
from flightanalysis.analysis.manoeuvre_analysis import Analysis
from loguru import logger
from joblib import Parallel, delayed
import os
import numpy as np
import pandas as pd


class ScheduleAnalysis(Collection):
    VType = Analysis
    uid = "name"

    @property
    def flown(self):
        return State.stack([m.flown for m in self])

    @property
    def template(self):
        return State.stack([m.template for m in self])

    @staticmethod
    def parse_ajson(ajson: AJson, sdef: SchedDef = None) -> ScheduleAnalysis:
        if not all([ajson.mdef for ajson in ajson.mans]) and sdef is None:
            raise ValueError("All manoeuvres must have a definition")
        analyses = []
        if sdef is None:
            sdef = [ManDef.from_dict(man.mdef) for man in ajson.mans]
        for man, mdef in zip(ajson.mans, sdef):
            analyses.append(Analysis.from_dict(man.model_dump() | dict(mdef=mdef.to_dict())))
        return ScheduleAnalysis(analyses)

    def run(
        self, optimise: bool = False, sync: boolean = False, throw_errors: bool = False, subset: list = None
    ) -> Self:
        if subset is None:
            subset = range(len(self))

        logger.info(f"Starting {os.cpu_count()} ma processes")
        if sync:
            madicts = [
                Analysis.parse_analyse_serialise(man.to_dict(), optimise, throw_errors)
                for i, man in enumerate(self)
                if i in subset
            ]
        else:
            madicts = Parallel(n_jobs=os.cpu_count() * 2 - 1)(
                delayed(Analysis.parse_analyse_serialise)(man.to_dict(), optimise, throw_errors)
                for i, man in enumerate(self)
                if i in subset
            )

        return ScheduleAnalysis(
            [
                Analysis.from_dict(madicts[subset.index(i)])
                if i in subset
                else self[i]
                for i in range(len(self))
            ]
        )


    def scores(self):
        scores = {}
        total = 0
        scores = {
            ma.name: (ma.scores.score() if hasattr(ma, "scores") and ma.scores else 0) for ma in self
        }
        total = sum([ma.mdef.info.k * v for ma, v in zip(self, scores.values())])
        return total, scores

    def summarydf(self):
        return pd.DataFrame(
            [m.scores.summary() if m.scores else {} for m in self]
        )

    def score_summary_df(self, difficulty=3, truncate=False):
        return pd.DataFrame(
            [
                ma.scores.score_summary(difficulty, truncate)
                if ma.scores
                else {}
                for ma in self
            ]
        )

    def basic(self, sdef: SchedDef = None, remove_labels: bool = True) -> Self:
        return ScheduleAnalysis(
            [
                man.basic(sdef[man.mdef.info.short_name] if sdef is not None else None, remove_labels)
                for man in self
            ]
        )

    @property
    def mnames(self):
        return [m.name for m in self]
    
    @property
    def fls(self):
        return {m.name: m.flown for m in self}
    
    @property
    def tps(self):
        return {m.name: m.template for m in self}