from typing import NamedTuple
from collections import namedtuple
from pathlib import Path
from flightanalysis.base.utils import parse_csv, tryval, all_subclasses
from flightanalysis.scoring.criteria.exponential import free
from .criteria import Criteria
from . import AnyInterCriteria, AnyIntraCriteria


def parse_criteria_csv(file: str | Path, lookups: NamedTuple):
    df = parse_csv(file, sep=";")

    subclasses = {cls.__name__: cls for cls in all_subclasses(Criteria)}

    criteria: dict[str, dict[str, AnyInterCriteria | AnyIntraCriteria]] = {}
    for grpname, grp in df.groupby("group"):
        criteria[grpname] = {}
        for row in grp.itertuples(index=False):
            args = []
            for arg in row.args.split(","):
                if len(arg.strip()):
                    args.append(tryval(arg.strip()))
                else:
                    args.append(None)

            while len(args) and args[-1] is None:
                args.pop()

            lookup = (
                free
                if row.lookup == "free"
                else getattr(getattr(lookups, grpname), row.lookup)
            )

            criteria[grpname][row.name] = subclasses[row.kind](
                row.name,
                lookup,
                *args,
            )
    return namedtuple("Criteria", criteria.keys())(
        *[namedtuple(k, v.keys())(**v) for k, v in criteria.items()]
    )
