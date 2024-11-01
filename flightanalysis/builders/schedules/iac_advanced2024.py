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
    ScheduleInfo
)
from flightanalysis.builders.IAC.manbuilder import iacmb
from flightanalysis.builders.manbuilder import MBTags, c45, centred, r

sdef = SchedDef(
    [
        iacmb.create(
            ManInfo(
                "Double Humpty",
                "dHump",
                k=35,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.CROSS, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.loop(r(0.25)),
                iacmb.line(),
                iacmb.loop(r(0.5)),
                iacmb.snap(r(3/4)),
                iacmb.loop(r(0.5)),
                iacmb.roll(r(0.25)),
                iacmb.loop(r(-0.25)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Figure P",
                "fP",
                k=33,
                position=Position.CENTRE,
                start=BoxLocation(Height.TOP, Direction.CROSS, Orientation.INVERTED),
                end=BoxLocation(Height.MID, Direction.DOWNWIND),
            ),
            [
                iacmb.spin(r(1.25)),
                iacmb.line(length=70),
                iacmb.loop(r(3 / 4)),
                iacmb.roll('4x2', padded=False),
            ]
        ),
        iacmb.create(
            ManInfo(
                "Rolling Circle",
                "rCirc",
                k=23,
                position=Position.END,
                start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
                end=BoxLocation(Height.MID),
            ),
            [
                iacmb.loop(r(1/2), rolls=r(2), ke=True, radius=150),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Humpty",
                "hB",
                k=22,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(-0.25)),
                iacmb.line(),
                centred(iacmb.loop(r(-0.5), radius=50)),
                iacmb.roll("2x4"),
                iacmb.loop(r(0.25)),
            ]
        ),
        iacmb.create(
            ManInfo(
                "StallTurn",
                "sT",
                k=38,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(1/4)),
                iacmb.roll('3/4'),
                iacmb.stallturn(),
                iacmb.snap(r(0.5)),
                iacmb.loop(r(1/4)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "humpty",
                "hB2",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.CROSS, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(1/4)),
                iacmb.roll('2x4'),  
                iacmb.loop(r(1/2)),
                iacmb.roll(r(3/4)),
                iacmb.loop(r(1/4)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "Figure N",
                "fN",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.loop(r(1/2)),
                iacmb.roll(r(1/2)),
                iacmb.loop(r(3/8)),
                iacmb.snap(r(1)),
                iacmb.loop(r(-3/8)),
                iacmb.line(),
                iacmb.loop(r(-1/4))
            ],
        ),
        iacmb.create(
            ManInfo(
                "double humpty",
                "dhump2",
                k=33,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(-1/4)),
                iacmb.roll(r(1/4)),
                iacmb.loop(r(1/2)),
                iacmb.roll('2x8'),
                iacmb.loop(r(1/2)),
                iacmb.line(),
                iacmb.loop(r(1/4)),
            ]
        ),
        iacmb.create(
            ManInfo(
                "immelman",
                "imm",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                iacmb.roll(r(1), padded=False),
                iacmb.loop(r(1/2)),
                iacmb.roll([0.25,0.25,0.25,0.25,-0.5,-0.5], padded=False),
            ],
        ),
    ]
)


if __name__ == "__main__":
    sdef.plot().show()
    #sdef.create_fcj('BAeA Power Advanced 2024', 'baea_advanced.json')
    #sdef.to_json("flightanalysis/data/iac_advanced2024_schedule.json", ScheduleInfo('iac', 'advenced2024'))
