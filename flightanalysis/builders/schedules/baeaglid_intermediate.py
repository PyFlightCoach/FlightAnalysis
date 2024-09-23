import numpy as np

from flightanalysis import (
    BoxLocation,
    Direction,
    Height,
    ManInfo,
    Orientation,
    Position,
    SchedDef,
)
from flightanalysis.builders.BAeAGlid.downgrades import dggrps
from flightanalysis.builders.BAeAGlid.manbuilder import f3amb
from flightanalysis.builders.manbuilder import MBTags, c45, centred, r

sdef = SchedDef(
    [
        f3amb.create(
            ManInfo(
                "Half Roll",
                "hroll",
                k=8,
                position=Position.CENTRE,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                centred(f3amb.roll(np.pi, padded=False)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Split S",
                "S",
                k=6,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(np.pi),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Shark Fin",
                "Sfin",
                k=21,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(np.pi/4),
                f3amb.roll(np.pi),
                f3amb.loop(3*np.pi/4),
                f3amb.line(),
                f3amb.loop(np.pi/2),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Roll",
                "roll",
                k=14,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                centred(f3amb.roll(np.pi*2, padded=False)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Half Cuban Eight",
                "hCuban",
                k=16,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(5*np.pi/4),
                f3amb.roll(np.pi),
                f3amb.loop(np.pi/4),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Q Loop",
                "qloop",
                k=11,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                f3amb.loop(np.pi/4),
                f3amb.line(),
                centred(f3amb.loop(7*np.pi/4)),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Stallturn",
                "st",
                k=17,
                position=Position.END,
                start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(np.pi/2),
                f3amb.line(),
                f3amb.stallturn(),  
                f3amb.line(),
                f3amb.loop(np.pi/2),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Humpty Bump",
                "hb",
                k=15,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                f3amb.loop(np.pi/2),
                f3amb.line(),
                centred(f3amb.loop(-np.pi)),  
                f3amb.line(),
                f3amb.loop(np.pi/2),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Immelman",
                "imm",
                k=12,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                f3amb.loop(np.pi),
                f3amb.roll(np.pi, padded=False),
            ],
        ),
        f3amb.create(
            ManInfo(
                "Half Cuban 2",
                "hcub2",
                k=16,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                f3amb.loop(-np.pi/4),
                f3amb.line(),
                f3amb.loop(5*np.pi/4),
                f3amb.roll(np.pi, padded=False),
            ],
        ),
    ]
)



if __name__ == "__main__":
    sdef.plot().show()

    sdef.to_json("flightanalysis/data/BAeAGlid_intermediate.json")

