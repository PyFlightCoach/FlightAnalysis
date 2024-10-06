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
from flightanalysis.builders.IAC.manbuilder import iacmb
from flightanalysis.builders.manbuilder import MBTags, c45, centred, r

sdef = SchedDef(
    [
        iacmb.create(
            ManInfo(
                "Double Humpty",
                "dHump",
                k=37,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.loop(r(0.25)),
                iacmb.roll('2x8'),
                iacmb.loop(r(0.5)),
                iacmb.snap(r(3/4)),
                iacmb.loop(r(0.5)),
                iacmb.line(),
                iacmb.loop(r(-0.25)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Sharks Tooth",
                "sTooth",
                k=27,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.spin(r(1.5)),
                iacmb.line(length=70),
                iacmb.loop(r(3 / 8)),
                iacmb.roll('4x8', line_length=200),
                iacmb.loop(r(1 / 8)),
            ]
        ),
        iacmb.create(
            ManInfo(
                "Split S",
                "splitS",
                k=23,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.roll(r(1/2), padded=False),
                iacmb.loop(r(-0.5), radius=150),
                iacmb.roll(r([1/4, 1/4, 1/4, -1/8, -1/8]), padded=False),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Tail Slide",
                "TaSi",
                k=15,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(0.25)),
                iacmb.line(),
                centred(iacmb.loop(r(-0.5), radius=20)),
                iacmb.line(),
                iacmb.loop(r(0.25)),
            ]
        ),
        iacmb.create(
            ManInfo(
                "Immelman",
                "Imm",
                k=37,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                iacmb.roll('2x2', padded=False),
                iacmb.loop(r(1/2)),
                iacmb.roll(r([1.5,-1]), rolltypes='sr', padded=False),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Rolling Turn",
                "rtr",
                k=22,
                position=Position.CENTRE,
                start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                MBTags.CENTRE,
                iacmb.loop(r(1/2), rolls=r(2), ke=True, radius=150),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Half Cuban",
                "hcub",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.roll('4x2', padded=False),
                iacmb.loop(r(5/8)),
                iacmb.roll('2x4', line_length=300),
                iacmb.loop(r(1/8)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Stallturn",
                "sTrn",
                k=33,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(1/4)),
                iacmb.roll('3x4'),
                iacmb.stallturn(),
                iacmb.roll(r(3/4)),
                iacmb.loop(r(1/4)),
            ]
        ),
        iacmb.create(
            ManInfo(
                "Figure P",
                "fP",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                iacmb.loop(r(1/4)),
                iacmb.roll(r(1/2)),
                iacmb.loop(r(3/4)),
                iacmb.roll('4x4', padded=False),  
            ],
        ),
        iacmb.create(
            ManInfo(
                "Lay Down Humpty",
                "lhump",
                k=36,
                position=Position.END,
                start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(1/8)),
                iacmb.roll(r(1)),
                iacmb.loop(r(1/2)),
                iacmb.roll(r(1/2)),
                iacmb.loop(r(1/8)),
            ]
        ),
    ]
)


if __name__ == "__main__":
    #sdef.plot().show()
    #sdef.create_fcj('BAeA Power Advanced 2024', 'baea_advanced.json')
    sdef.to_json("flightanalysis/data/baeapower_advanced2024_schedule.json")
