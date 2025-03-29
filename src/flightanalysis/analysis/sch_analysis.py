from __future__ import annotations
from re import sub
import traceback
from xmlrpc.client import boolean
from flightdata import State
from typing import Self
from flightdata import Collection
from flightanalysis import ManDef, SchedDef
from schemas import AJson
from . import manoeuvre_analysis as ma
from loguru import logger
from joblib import Parallel, delayed
import os
import numpy as np
import pandas as pd


class ScheduleAnalysis(Collection):
    VType = ma.Analysis
    uid = "name"

    @property
    def flown(self):
        return State.stack([m.flown for m in self])

    @property
    def template(self):
        return State.stack([m.template for m in self])

    def proceed(self):
        return ScheduleAnalysis([m.proceed() for m in self])

    @staticmethod
    def parse_ajson(ajson: AJson, sdef: SchedDef = None) -> ScheduleAnalysis:
        if not all([ajson.mdef for ajson in ajson.mans]) and sdef is None:
            raise ValueError("All manoeuvres must have a definition")
        analyses = []
        if sdef is None:
            sdef = [ManDef.from_dict(man.mdef) for man in ajson.mans]
        for man, mdef in zip(ajson.mans, sdef):
            analyses.append(ma.from_dict(man.model_dump() | dict(mdef=mdef.to_dict())))
        return ScheduleAnalysis(analyses)

    def run_all(
        self, optimise: bool = False, sync: boolean = False, subset: list = None
    ) -> Self:
        if subset is None:
            subset = range(len(self))

        def parse_analyse_serialise(pad):
            import tuning
            try:
                pad = ma.from_dict(pad)
            except Exception as e:
                logger.exception(f"Failed to parse {pad['id']}")
                return pad

            try:
                pad = pad.run_all(optimise)
                logger.info(f"Completed {pad.name}")
                return pad.to_dict()
            except Exception as e:
                logger.exception(f"Failed to process {pad.name}")
                return pad.to_dict()

        logger.info(f"Starting {os.cpu_count()} ma processes")
        if sync:
            madicts = [
                parse_analyse_serialise(man.to_dict())
                for i, man in enumerate(self)
                if i in subset
            ]
        else:
            madicts = Parallel(n_jobs=os.cpu_count() * 2 - 1)(
                delayed(parse_analyse_serialise)(man.to_dict())
                for i, man in enumerate(self)
                if i in subset
            )

        return ScheduleAnalysis(
            [
                ma.Scored.from_dict(madicts[subset.index(i)])
                if i in subset
                else self[i]
                for i in range(len(self))
            ]
        )

    def run_all_sync(self, optimise: bool = False, force: bool = False) -> Self:
        return ScheduleAnalysis([ma.run_all(optimise, force) for ma in self])

    def optimize_alignment(self) -> Self:
        def parse_analyse_serialise(mad):
            an = ma.Complete.from_dict(mad)
            return an.run_all().to_dict()

        logger.info(f"Starting {os.cpu_count()} alignment optimisation processes")

        madicts = Parallel(n_jobs=os.cpu_count())(
            delayed(parse_analyse_serialise)(man.to_dict()) for man in self
        )
        return ScheduleAnalysis([ma.from_dict(mad) for mad in madicts])

    def scores(self):
        scores = {}
        total = 0
        scores = {
            ma.name: (ma.scores.score() if hasattr(ma, "scores") else 0) for ma in self
        }
        total = sum([ma.mdef.info.k * v for ma, v in zip(self, scores.values())])
        return total, scores

    def summarydf(self):
        return pd.DataFrame(
            [ma.scores.summary() if hasattr(ma, "scores") else {} for ma in self]
        )
