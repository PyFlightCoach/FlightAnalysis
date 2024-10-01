import numpy as np

from flightanalysis import (
    BoxLocation,
    Direction,
    Height,
    ManInfo,
    Orientation,
    Position,
    SchedDef,
    ManParm,
    Combination,
)
from flightanalysis.builders.IAC.downgrades import dggrps
from flightanalysis.builders.IAC.manbuilder import iacmb
from flightanalysis.builders.manbuilder import MBTags, c45, centred, r

sdef = SchedDef(
    [
        iacmb.create(
            ManInfo(
                "Double Humpty",
                "dHump",
                k=53,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.loop(r(0.25)),
                iacmb.snap(r(0.5)),
                iacmb.loop(r(-0.5)),
                iacmb.roll("2x4"),
                iacmb.loop(r(0.5)),
                iacmb.snap(r(0.5)),
                iacmb.loop(r(-0.25)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Sharks Tooth",
                "sTooth",
                k=41,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.spin("rsdir[0]"),
                iacmb.snap("rsdir[1]"),
                iacmb.loop(r(3 / 8)),
                iacmb.roll(r(1)),
                iacmb.loop(r(-1 / 8)),
            ],
            rsdir=ManParm(
                "rsdir", Combination(desired=r([[1.25, 0.75], [-1.25, -0.75]])), 0, "rad"
            ),
        ),
        iacmb.create(
            ManInfo(
                "Split S",
                "splitS",
                k=36,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.roll(r(1), padded=False),
                iacmb.loop(r(-0.5)),
                iacmb.roll(r([1.25, -1.75]), padded=False),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Tail Slide",
                "TS",
                k=34,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(0.5)),
                iacmb.snap(r(0.75)),
                iacmb.loop(r(-0.5)),
                iacmb.roll('2x8'),
                iacmb.loop(r(-0.5)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Horisontal Eight",
                "H8",
                k=58,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(-1/8)),
                iacmb.roll('4x8'),
                iacmb.loop(r(-3/4)),
                iacmb.snap(1, break_angle=np.radians(-10)),  
                iacmb.loop(r(5/8)),
                iacmb.roll(2, padded=False),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Sharks Tooth 2",
                "sk2",
                k=44,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(1/8)),
                iacmb.roll(r([0.125, 0.125, -0.75]), rolltypes='rrs'),
                iacmb.loop(r(3/8)),
                iacmb.roll('4x4'),  
                iacmb.loop(r(1/4)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Figure P",
                "fP",
                k=46,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                iacmb.loop(r(1/4)),
                iacmb.roll('4x8'),
                iacmb.loop(r(3/4), rolls='8x8'),
                iacmb.roll(r([1/8, 1/8, -1/4]), padded=False),  
            ],
        ),
        iacmb.create(
            ManInfo(
                "Rolling Circle",
                "rCirc",
                k=34,
                position=Position.END,
                start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.INVERTED),
                end=BoxLocation(Height.MID),
            ),
            [
                iacmb.loop(r(3/4), rolls=r([1.5]), ke=True),
            ]
        ),
        iacmb.create(
            ManInfo(
                "Double Humpty 2",
                "dHump2",
                k=41,
                position=Position.CENTRE,
                start=BoxLocation(Height.MID, Direction.CROSS, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            ),
            [
                iacmb.loop(r(1/4)),
                iacmb.line(),
                iacmb.loop(r(1/2)),
                iacmb.snap(r(1)),  
                iacmb.loop(r(1/2)),
                iacmb.roll(r(3/4)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Lay Down Humpty",
                "lhump",
                k=36,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.loop(r(1/8)),
                iacmb.roll('4x8'),
                iacmb.loop(r(1/2)),
                iacmb.snap(r(0.5), break_angle=np.radians(-10)),
                iacmb.loop(r(-1/4)),
            ]
        ),
    ]
)


if __name__ == "__main__":
    sdef.plot().show()

#    sdef.to_json("flightanalysis/data/BAeAGlid_intermediate.json")
