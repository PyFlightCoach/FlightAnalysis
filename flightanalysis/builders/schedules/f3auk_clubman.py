"""
UKF3A Clubman template
Author Vince Beesley
"""

import numpy as np

from flightanalysis import (
    BoxLocation,
    Combination,
    Direction,
    Height,
    ManInfo,
    ManParm,
    Orientation,
    Position,
    SchedDef,
)

from flightanalysis.builders.f3a.manbuilder import f3amb
from flightanalysis.builders.manbuilder import MBTags, c45, centred, r

sdef = SchedDef(
    [
        f3amb.create(
            ManInfo(
                "Inside Loop",
                "loop",
                k=2,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                MBTags.CENTRE,
                f3amb.loop(r(2), radius=100),
                MBTags.CENTRE,
            ],
        ),
        f3amb.create(
            ManInfo(
                "Half Rev Cuban 8",
                "rcub",
                k=2,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(1 / 8)),
                centred(f3amb.roll(r(1 / 2), line_length=2 * 65)),
                f3amb.loop(r(5 / 8)),
            ],
            loop_radius=65,
        ),
        f3amb.create(
            ManInfo(
                "slow Roll",
                "roll",
                k=3,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                centred(f3amb.roll(r(2), full_rate=np.pi, padded=False)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Half Cuban 8",
                "hcub2",
                k=2,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(5 / 8)),
                centred(f3amb.roll(r(1 / 2), line_length=2 * 65)),
                f3amb.loop(r(1 / 8)),
            ],
            loop_radius=65,
        ),
        f3amb.create(
            ManInfo(
                "Immelman combo",
                "Imm",
                k=3,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(1 / 2)),
                f3amb.roll(r(1 / 2), padded=False),
                f3amb.line(length=30),
                f3amb.roll(r(1 / 2), padded=False),
                f3amb.loop(r(1 / 2)),
            ],
            loop_radius=70,
        ),
        f3amb.create(
            ManInfo(
                "Humpty",
                "hB",
                k=2,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(1 / 4)),
                f3amb.roll(r(1 / 2)),
                f3amb.loop(r(1 / 2)),
                f3amb.line(),
                f3amb.loop(r(1 / 4)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Inverted Flight",
                "inv",
                k=2,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.roll(r(1 / 2), padded=False),
                f3amb.line(length=100),
                f3amb.roll(r(1 / 2), padded=False),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Stall Turn",
                "st",
                k=3,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(1 / 4)),
                f3amb.line(),
                f3amb.stallturn(),
                f3amb.line(),
                f3amb.loop(r(1 / 4)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Outside Loop",
                "oloop",
                k=3,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.roll(r(1 / 2), padded=False),
                f3amb.line(length="ee_pause"),
                MBTags.CENTRE,
                f3amb.loop(-r(1), radius=100),
                MBTags.CENTRE,
                f3amb.line(length="ee_pause"),
                f3amb.roll(r(1 / 2), padded=False),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Outer Humpty",
                "ohB",
                k=2,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(1 / 4)),
                f3amb.line(),
                f3amb.loop(r(1 / 2)),
                f3amb.roll(r(1 / 2)),
                f3amb.loop(r(1 / 4)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Cuban 8",
                "c8",
                k=2,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(5 / 8)),
                centred(f3amb.roll(r(1 / 2))),
                f3amb.loop(r(3 / 4)),
                centred(f3amb.roll(r(1 / 2))),
                f3amb.loop(r(1 / 8)),
            ],
            loop_radius=100,
            line_length=200,
        ),
        f3amb.create(
            ManInfo(
                "Half Sqr Loop",
                "hsql",
                k=2,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(r(1 / 4)),
                centred(f3amb.roll(r(1 / 2))),
                f3amb.loop(-r(1 / 4)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "3 Turn Spin",
                "spin",
                k=3,
                position=Position.CENTRE,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                MBTags.CENTRE,
                f3amb.spin(r(3)),
                f3amb.line(),
                f3amb.loop(r(1 / 4)),
            ],
        ),
    ]
)


if __name__ == "__main__":
    from flightanalysis import Heading, ManDef, Manoeuvre
    from flightplotting import plot_regions
    mdef: ManDef = sdef.spin
    itrans = mdef.guess_itrans(170, Heading.RTOL)
    mdef = mdef.fit_box(itrans)
    man: Manoeuvre = mdef.create()
    tp = man.create_template(itrans)
    fig = plot_regions(tp, 'element')
    fig.add_traces(mdef.box.plot())
    fig.show()
#    sdef.plot().show()
#    clubman_def.to_json("flightanalysis/data/f3auk_clubman_schedule.json")

#    import os
#    clubman_def.create_fcjs('f3auk_clubman', f'{os.environ['HOME']}/Desktop/templates/')
