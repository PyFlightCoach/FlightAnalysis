from flightanalysis import (
    ScheduleInfo,
    logger,
    enable_logging,
    __version__,
    Heading,
    Direction,
)
from flightanalysis.analysis.analysis_json import AnalysisJson
from flightanalysis.analysis.manoeuvre_analysis import MA
from pathlib import Path
from flightdata import Flight, fcj, Origin, State, FCJOrigin
from joblib import Parallel, delayed
import os
import argparse
import traceback


def _create_state(fcjson: fcj.FCJ, bin: Path | None, origin: Origin):
    fl = Flight.from_log(bin) if bin else Flight.from_fc_json(fcjson)
    return fl.boot_time() or fcjson.created, State.from_flight(fl, origin)


def create_ajson(fcjson: fcj.FCJ, bin: Path = None, ajs: Path = None) -> AnalysisJson:
    sinfo = ScheduleInfo(*fcjson.parameters.schedule).fcj_to_pfc()
    mdetails = sinfo.manoeuvre_details()
    origin = Origin.from_fcjson_parameters(fcjson.parameters)
    tboot, st = _create_state(fcjson, bin, origin)
    try:
        aj = AnalysisJson.model_validate_json(ajs.open().read()) if ajs else None
    except Exception:
        aj = None

    ddef = sinfo.direction_definition()

    schedule_direction = Direction.parse(ddef["direction"]).wind_swap_heading(
        Heading.infer(
            st[
                fcjson.data[fcjson.mans[ddef["manid"] + 1].start].time / 1e6
            ].att.bearing()[0]
        )
    )

    return AnalysisJson(
        origin=FCJOrigin(
            lat=origin.lat,
            lng=origin.long,
            alt=origin.alt,
            heading=origin.heading,
        ),
        isComp=aj.isComp if aj else True,
        sourceBin=bin.name if bin and bin.exists() else None,
        sourceFCJ=fcjson.name,
        bootTime=tboot if tboot else aj.bootTime,
        mans=[
            MA(
                name=mdetails[i].name,
                id=i + 1,
                schedule=sinfo,
                schedule_direction=schedule_direction.name,
                flown=st[
                    fcjson.data[man.start].time / 1e6 : fcjson.data[man.stop].time / 1e6
                ].to_dict(),
                history={
                    res.fa_version: res.manresults[i + 1]
                    for res in fcjson.fcs_scores
                    if res.manresults[i + 1]
                }
                | (aj.mans[i].history if (aj and aj.mans[i].history) else {}),
            ).simplify_history()
            for i, man in enumerate(fcjson.mans[1:-1])
        ],
    )


def run_dict(mdict):
    logger.info(f"Running {mdict['name']}")
    man = MA.model_validate(mdict).run(True, True, False).model_dump()
    logger.info(f"Completed {mdict['name']}")
    return man


def run_analysis(ajson: AnalysisJson, parallel: bool = True):
    return AnalysisJson(
        **(
            ajson.__dict__
            | dict(
                mans=(
                    [
                        MA.model_validate(oman)
                        for oman in Parallel(n_jobs=os.cpu_count())(
                            delayed(run_dict)(man.model_dump()) for man in ajson.mans
                        )
                    ]
                    if parallel
                    else [man.run(True, True, False) for man in ajson.mans]
                )
            )
        )
    )


def analyse_log(fcjson: Path, refresh: bool = False, parallel: bool = True):
    bin = fcjson.parent / f"{fcjson.stem[-8:]}.BIN"
    ajs = fcjson.parent / f"{fcjson.stem[-8:]}.ajson"
    logger.info(f"Processing {fcjson}")
    logger.info(f"BIN: {bin}")

    if not ajs.exists() or refresh:
        logger.info(f"{'Creating' if not refresh else 'Refreshing'} analysis json")
        aj = create_ajson(
            fcj.FCJ.model_validate_json(fcjson.open().read()),
            bin if bin.exists() else None,
            ajs if ajs.exists() else None,
        )
    else:
        logger.info(f"Parsing: {ajs}")
        aj = AnalysisJson.model_validate_json(ajs.open().read())

    if not aj.check_version(__version__) or refresh:
        if not aj.check_version(__version__):
            aj = run_analysis(aj, parallel)
        with open(ajs, "w") as f:
            f.write(aj.model_dump_json(indent=2))

    print(aj.create_score_df(fcj.ScoreProperties(difficulty=3, truncate=False)).T)


def analyse_logs(folder: Path, refresh: bool = False, parallel: bool = True):
    fcjs = list(folder.rglob("*.json"))

    for i, fcjson in enumerate(fcjs):
        logger.info(f"Processing {i} of {len(fcjs)} {fcjson}")
        try:
            analyse_log(fcjson, refresh, parallel)
        except Exception as e:
            logger.error(f"Error processing {fcjson}: {e}")
            logger.info(traceback.format_exc())


def main():
    enable_logging("INFO")

    parser = argparse.ArgumentParser(description="Analyse all flight coach jsons")
    parser.add_argument(
        "-f", "--folder", default=".", help="Source directory, defaults to current"
    )

    parser.add_argument(
        "-r",
        "--refresh",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="refresh analysis for current version if already exists",
    )

    args = parser.parse_args()
    analyse_logs(Path(args.folder), args.refresh)


if __name__ == "__main__":
    main()
#    analyse_log(
#        Path(
#            '~/OneDrive/proj/logs/2023_12_20/manual_F3A_F25_23_12_20_00000157.json'
#        ).expanduser(),
#        True, False
#    )
