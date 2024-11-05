from flightanalysis import ScheduleInfo, enable_logging, SchedDef, Direction, Heading
from importlib import import_module
from pathlib import Path
import argparse


def main():
    logger = enable_logging("INFO")

    parser = argparse.ArgumentParser(description="Create Schedule Definitions")
    parser.add_argument(
        "-s", "--search", default="*", help="search string for schedule"
    )

    parser.add_argument(
        "-p",
        "--plot",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="plot the schedule",
    )

    parser.add_argument(
        "-c",
        "--create",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="create the definition",
    )

    parser.add_argument(
        "-t",
        "--target",
        default="flightanalysis/data",
        help="target folder to write sdefs to",
    )

    args = parser.parse_args()

    schedules = [
        p
        for p in Path("flightanalysis/builders/schedules").glob(f"{args.search}.py")
        if "__" not in str(p)
    ]

    for s in schedules:
        sinfo = ScheduleInfo.from_str(s.stem)
        logger.info(str(sinfo))
        if True:  # args.plot or args.create:
            sdef: SchedDef = import_module(
                str(s).replace("/", ".").replace(".py", "")
            ).sdef
            wdman = sdef.wind_def_manoeuvre()
            logger.info(wdman)

            if args.create:
                sdef.to_json(Path(args.target) / f"{str(sinfo)}_schedule.json", sinfo)

            if args.plot:
                fig = sdef.plot(
                    sdef[0].box.middle().y[0],
                    Heading.INTOOUT
                    if sdef[0].info.start.direction == Direction.CROSS
                    else Heading.LTOR,
                )
                fig.add_traces(sdef[0].box.plot())
                fig.show()

# def create_all():
#    for k, sdef in sdefs.items():
#
#        sdef.to_json(f"flightanalysis/data/{k}.json", ScheduleInfo.from_str(k))

if __name__ == "__main__":
    main()
