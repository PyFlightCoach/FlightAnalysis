from __future__ import annotations
from typing import Self, Union
from json import load, dump
from flightdata import Flight, State, Origin, Collection, NumpyEncoder, fcj
from flightanalysis.definition import SchedDef, ScheduleInfo, Heading
from flightanalysis import __version__
from . import manoeuvre_analysis as ma
from loguru import logger
from joblib import Parallel, delayed
import os
import numpy as np
import pandas as pd


class ScheduleAnalysis(Collection):
    VType = ma.Analysis
    uid = "name"

    @staticmethod
    def from_fcj(
        fcj: fcj.FCJ,
        flight: Flight | None = None,
        proceed=True,
    ) -> ScheduleAnalysis:
        flight = flight if flight else Flight.from_fc_json(fcj)

        info = ScheduleInfo(*fcj.parameters.schedule).fcj_to_pfc()
        sdef = SchedDef.load(info)
        box = Origin.from_fcjson_parameters(fcj.parameters)

        state = State.from_flight(flight, box)

        state = state.splitter_labels(fcj.mans, sdef.uids, t0=fcj.data[0].time / 1e6)

        heading = Heading.infer(state.get_manoeuvre(sdef[0].uid)[0].att.bearing()[0])

        mas = []
        for i, mdef in enumerate(sdef):
            st = state.get_manoeuvre(mdef.uid)

            if fcj.fcs_scores and len(fcj.fcs_scores) > 0:
                st = st.label_els(fcj.fcs_scores[-1].manresults[i + 1].els)

            nma = ma.Basic(
                mdef.info.short_name,
                i,
                info,
                mdef,
                st,
                mdef.info.start.direction.wind_swap_heading(heading),
                None,
            )
            if proceed:
                nma = nma.proceed()
            mas.append(nma)

        return ScheduleAnalysis(mas, info)

    def append_scores_to_fcj(self, file: Union[str, dict], ofile: str = None) -> dict:
        data = file if isinstance(file, dict) else load(open(file, "r"))

        new_results = dict(
            fa_version=__version__,
            manresults=[None]
            + [
                man.fcj_results() if hasattr(man, "fcj_results") else None
                for man in self
            ],
        )

        if "fcs_scores" not in data:
            data["fcs_scores"] = []

        for res in data["fcs_scores"]:
            if res["fa_version"] == new_results["fa_version"]:
                res["manresults"] = new_results["manresults"]
                break
        else:
            data["fcs_scores"].append(new_results)

        if "jhash" in data:
            del data["jhash"]

        if ofile:
            dump(
                data,
                open(file if ofile == "same" else ofile, "w"),
                cls=NumpyEncoder,
                indent=2,
            )

        return data

    def run_all(self) -> Self:
        def parse_analyse_serialise(pad):
            try:
                pad = ma.from_dict(pad).run_all()
                pad = pad.run_all()
                logger.info(f"Completed {pad.name}")
            except Exception as e:
                logger.error(f"Failed to process {pad.name}: {repr(e)}")
            return pad.to_dict()

        logger.info(f"Starting {os.cpu_count()} ma processes")
        madicts = Parallel(n_jobs=os.cpu_count())(
            delayed(parse_analyse_serialise)(man.to_dict()) for man in self
        )

        return ScheduleAnalysis([ma.Scored.from_dict(mad) for mad in madicts])

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
