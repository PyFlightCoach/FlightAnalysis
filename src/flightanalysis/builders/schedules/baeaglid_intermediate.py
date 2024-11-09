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

from flightanalysis.builders.BAeAGlid.manbuilder import glidmb
from flightanalysis.builders.manbuilder import MBTags, c45, centred, r

sdef = SchedDef(
    [
        glidmb.create(
            ManInfo(
                "Half Roll",
                "hroll",
                k=8,
                position=Position.CENTRE,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                centred(glidmb.roll(np.pi, padded=False)),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Split S",
                "S",
                k=6,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
                end=BoxLocation(Height.BTM),
            ),
            [
                glidmb.loop(np.pi),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Shark Fin",
                "Sfin",
                k=21,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                glidmb.loop(np.pi/4),
                glidmb.roll(np.pi),
                glidmb.loop(3*np.pi/4),
                glidmb.line(),
                glidmb.loop(np.pi/2),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Roll",
                "roll",
                k=14,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                centred(glidmb.roll(np.pi*2, padded=False)),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Half Cuban Eight",
                "hCuban",
                k=16,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                glidmb.loop(5*np.pi/4),
                glidmb.roll(np.pi),
                glidmb.loop(np.pi/4),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Q Loop",
                "qloop",
                k=11,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.MID),
            ),
            [
                glidmb.loop(np.pi/4),
                glidmb.line(),
                centred(glidmb.loop(7*np.pi/4)),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Stallturn",
                "st",
                k=17,
                position=Position.END,
                start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                glidmb.loop(np.pi/2),
                glidmb.line(),
                glidmb.stallturn(),  
                glidmb.line(),
                glidmb.loop(np.pi/2),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Humpty Bump",
                "hb",
                k=15,
                position=Position.CENTRE,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.BTM),
            ),
            [
                glidmb.loop(np.pi/2),
                glidmb.line(),
                centred(glidmb.loop(-np.pi)),  
                glidmb.line(),
                glidmb.loop(np.pi/2),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Immelman",
                "imm",
                k=12,
                position=Position.END,
                start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                glidmb.loop(np.pi),
                glidmb.roll(np.pi, padded=False),
            ],
        ),
        glidmb.create(
            ManInfo(
                "Half Cuban 2",
                "hcub2",
                k=16,
                position=Position.END,
                start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
                end=BoxLocation(Height.TOP),
            ),
            [
                glidmb.loop(-np.pi/4),
                glidmb.line(),
                glidmb.loop(5*np.pi/4),
                glidmb.roll(np.pi, padded=False),
            ],
        ),
    ]
)



if __name__ == "__main__":
    sdef.plot().show()

    sdef.to_json("flightanalysis/data/BAeAGlid_intermediate.json")

