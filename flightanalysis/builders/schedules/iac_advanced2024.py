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
    ScheduleInfo,
    Heading
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
                iacmb.snap("roll_option[0]"),
                iacmb.loop(r(0.5)),
                iacmb.roll("roll_option[1]"),
                iacmb.loop(r(0.25)),
            ],
            roll_option=ManParm(
                "roll_option",
                Combination(desired=[r([3 / 4, 1 / 4]), r([-3 / 4, -1 / 4])]),
                1,
                "rad",
            ),
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
                iacmb.line(),
                iacmb.loop(r(3 / 4)),
                iacmb.roll("4x2", padded=False),
            ],
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
                iacmb.loop(
                    "roll_option[0]", rolls="roll_option[1]", ke=True, radius=150
                ),
            ],
            roll_option=ManParm(
                "roll_option",
                Combination(desired=[r([-0.5, -2]), r([0.5, 2])]),
                1,
                "rad",
            ),
        ),
        iacmb.create(
            ManInfo(
                "Humpty 1",
                "hB",
                k=22,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(-0.25)),
                iacmb.line(),
                centred(iacmb.loop(r(-0.5))),
                iacmb.roll("2x4"),
                iacmb.loop(r(0.25)),
            ],
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
                iacmb.loop(r(1 / 4)),
                iacmb.roll(r(-3/4)),
                iacmb.stallturn(),
                iacmb.snap(r(0.5)),
                iacmb.loop(r(1 / 4)),
            ],
        ),
        iacmb.create(
            ManInfo(
                "humpty 2",
                "hB2",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.CROSS, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(1 / 4)),
                iacmb.roll("2x4"),
                iacmb.loop(r(-1 / 2)),
                iacmb.roll(r(-3 / 4)),
                iacmb.loop(r(1 / 4)),
            ]
        ),
        iacmb.create(
            ManInfo(
                "Figure N",
                "fN",
                k=41,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                iacmb.loop(r(1 / 4), radius="loop_radius"),
                iacmb.roll(r(1 / 2), line_length=200),
                iacmb.loop(r(-3 / 8), radius="loop_radius"),
                iacmb.snap(r(1), line_length=400),
                iacmb.loop(r(3 / 8), radius="loop_radius"),
                iacmb.line(length=200),
                iacmb.loop(r(-1 / 4), radius="loop_radius"),
            ],
        ),
        iacmb.create(
            ManInfo(
                "double humpty",
                "dhump2",
                k=30,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                iacmb.loop(r(-1 / 4)),
                iacmb.roll("roll_option[0]"),
                iacmb.loop(r(1 / 2)),
                iacmb.roll(["roll_option[1]", "roll_option[1]"]),
                iacmb.loop(r(-1 / 2)),
                iacmb.line(),
                iacmb.loop(r(1 / 4)),
            ],
            roll_option=ManParm(
                "roll_option",
                Combination(
                    desired=[r([0.25, -0.125, -0.125]), r([-0.25, 0.125, 0.125])]
                ),
                1,
                "rad",
            ),
        ),
        iacmb.create(
            ManInfo(
                "immelman",
                "imm",
                k=34,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                iacmb.roll(r(1), padded=False),
                iacmb.loop(r(1 / 2)),
                iacmb.roll(r([0.25, 0.25, 0.25, 0.25, -0.5, -0.5]), padded=False),
            ],
        ),
    ]
)


if __name__ == "__main__":
    fig = sdef.plot(500, Heading.OUTTOIN, span=10)
    fig.add_traces(sdef[0].box.plot())
    fig.show()
    # sdef.create_fcj('BAeA Power Advanced 2024', 'baea_advanced.json')
    # sdef.to_json("flightanalysis/data/iac_advanced2024_schedule.json", ScheduleInfo('iac', 'advanced2024'))
