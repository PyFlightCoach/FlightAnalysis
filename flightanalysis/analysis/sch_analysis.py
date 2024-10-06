from __future__ import annotations
from typing import Self, Union
from json import load, dump
from flightdata import Flight, State, Origin, Collection, NumpyEncoder
from flightanalysis.definition import SchedDef, ScheduleInfo, Heading, ManDef
from flightanalysis import __version__
from . import manoeuvre_analysis as analysis
from loguru import logger
from joblib import Parallel, delayed
import os
import numpy as np
import pandas as pd


class ScheduleAnalysis(Collection):
    VType = analysis.Analysis
    uid = "name"

    @staticmethod
    def from_fcj(
        fcj: Union[str | bytes, dict],
        flight: Flight | None = None,
        proceed=True,
    ) -> ScheduleAnalysis:
        data = fcj if isinstance(fcj, dict) else load(open(fcj, "r"))

        flight = Flight.from_fc_json(data) if flight is None else flight

        info = ScheduleInfo(*data["parameters"]["schedule"]).fcj_to_pfc()
        sdef = SchedDef.load(info)
        box = Origin.from_fcjson_parameters(data["parameters"])

        state = State.from_flight(flight, box)

        state = state.splitter_labels(
            data["mans"], sdef.uids, t0=data["data"][0]["time"] / 1e6
        )

        heading = Heading.infer(state.get_manoeuvre(sdef[0].uid)[0].att.bearing()[0])

        mas = []
        for i, mdef in enumerate(sdef):
            st = state.get_manoeuvre(mdef.uid)

            if "fcs_scores" in data and len(data["fcs_scores"]) > 0:
                st = st.label_els(
                    list(data["fcs_scores"])[-1]["manresults"][i + 1]["els"]
                )

            nma = analysis.Basic(
                i, mdef, st, mdef.info.start.direction.wind_swap_heading(heading), None
            )
            if proceed:
                nma = nma.proceed()
            mas.append(nma)

        return ScheduleAnalysis(mas, info)

    @staticmethod
    def parse_analysis_json(data: str | dict) -> ScheduleAnalysis:
        if not isinstance(data, dict):
            data = load(open(data, "r"))

        sts = data["states"]["data"]
        entry = Heading.infer(State(sts[data["mans"][0]["start"]]).att.bearing()[0])

        mas = []
        for man in data["mans"]:
            mdef = ManDef.load(ScheduleInfo(**man["sinfo"]), man["name"])
            if not data["isComp"]:
                heading = Heading.infer(State(sts[man["start"]]).att.bearing()[0])
            else:
                heading = mdef.info.start.direction.wind_swap_heading(entry)

            st = (
                State.from_dict(sts[man["start"] : man["stop"]])
                .label(manoeuvre=man["name"])
                .label_els(list(man["history"].values())[-1]["els"])
            )

            mas.append(analysis.Basic(man["id"], mdef, st, heading, None))

        return ScheduleAnalysis(mas)

    def create_analysis_dict(self, **kwargs) -> dict:
        pass


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
                pad = analysis.parse_dict(pad)
                pad = pad.run_all()
                logger.info(f"Completed {pad.name}")
            except Exception as e:
                logger.error(f"Failed to process {pad.name}: {repr(e)}")
            return pad.to_dict()

        logger.info(f"Starting {os.cpu_count()} analysis processes")
        madicts = Parallel(n_jobs=os.cpu_count())(
            delayed(parse_analyse_serialise)(ma.to_dict()) for ma in self
        )

        return ScheduleAnalysis(
            [analysis.Scored.from_dict(mad) for mad in madicts]
        )

    def optimize_alignment(self) -> Self:
        def parse_analyse_serialise(mad):
            an = analysis.Complete.from_dict(mad)
            return an.run_all().to_dict()

        logger.info(f"Starting {os.cpu_count()} alinment optimisation processes")
        inmadicts = [mdef.to_dict() for mdef in self]
        madicts = Parallel(n_jobs=os.cpu_count())(
            delayed(parse_analyse_serialise)(mad) for mad in inmadicts
        )
        return ScheduleAnalysis(
            [analysis.Scored.from_dict(mad) for mad in madicts]
        )

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
