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
                "Stallturn",
                "sturn",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(0.125)),
                iacmb.roll(r(1.5)),
                iacmb.loop(r(-0.125)),
                iacmb.roll(r(0.25)),
                iacmb.stallturn(),
                iacmb.roll(r(1.75)),
                iacmb.loop(r(0.25)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Figure N",
                "N",
                k=30,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.loop(r(0.25)),
                iacmb.roll('2x4'),
                iacmb.loop(r(-3/8)),
                centred(iacmb.snap(r(1))),
                iacmb.loop(r(3/8)),
                iacmb.roll(r(1)),
                iacmb.loop(r(0.25)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Double Humpty",
                "dhump",
                k=30,
                position=Position.CENTRE,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.spin(r(1)),
                iacmb.line(),
                iacmb.loop(r(1/2)),
                iacmb.roll('2x8'),
                iacmb.loop(r(1/2)),
                iacmb.snap(r(0.75)),
                iacmb.loop(r(0.25)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Loop",
                "loop",
                k=30,
                position=Position.CENTRE,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(1), rolls='4x2', rollangle=np.radians(90)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "tailslide",
                "tside",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(0.25)),
                iacmb.roll(r(0.5)),
                iacmb.loop(r(-0.5), radius=20),
            ],
        ),
        iacmb.create(
            ManInfo(
                "immelman",
                "imm",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.roll(r([1,-1])),
                iacmb.loop(r(0.5)),
                iacmb.snap(r(1.5)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "rolling turn",
                "rtrn",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(0.25)),
                iacmb.roll(r(0.5)),
                iacmb.loop(r(-0.5), radius=20),
            ],
        ),
    ]
)


if __name__ == "__main__":
    sdef.plot().show()
    #sdef.create_fcj('BAeA Power Unlimited 2024', 'baea_unlim')
    #sdef.to_json("flightanalysis/data/baeapower_unlimited2024_schedule.json")
