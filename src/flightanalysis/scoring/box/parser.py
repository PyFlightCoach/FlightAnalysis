from typing import NamedTuple
from collections import namedtuple
from pathlib import Path
from flightanalysis.base.utils import parse_csv
from flightanalysis.scoring.box.box import BoxDG
from flightanalysis.scoring.reffuncs import measures
from tomllib import load
from .triangular_box import TriangularBox
from .rectangular_box import RectangularBox

def parse_box_downgrades(file: Path, box_criteria: NamedTuple):
    df = parse_csv(file, sep=";")


    boxdgs: dict[str, dict[str, BoxDG]] = {}
    for grpname, grp in df.groupby("kind"):
        boxdgs[grpname] = {}
        for row in grp.itertuples(index=False):
            boxdgs[grpname][row.name] = BoxDG(
                getattr(box_criteria, row.criteria),
                measures.parse_csv_cell(row.measure),

            )
    return namedtuple("BoxDGs", boxdgs.keys())(
        *[namedtuple(k, v.keys())(**v) for k, v in boxdgs.items()]
    )


def parse_box(toml: Path, box_dgs: NamedTuple):
    data = load(toml.open("rb"))

    Cls = TriangularBox if data["kind"] == "Triangular" else RectangularBox

    return Cls(
        data["width"],
        data["height"],
        data["depth"],
        data["distance"],
        data["floor"],
        {k: v for k, v in box_dgs.box._asdict().items()},
        box_dgs.centre.centre if hasattr(box_dgs, "centre") else None,
    )