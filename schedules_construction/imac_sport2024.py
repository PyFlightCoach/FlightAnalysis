from flightanalysis import SchedDef, ManInfo, BoxLocation, Position, Orientation, Height, Direction, imacmb, r
import numpy as np


c45 = np.cos(np.radians(45))

mps = imacmb.mps

sdef = SchedDef([
    imacmb.create(ManInfo(
            "Laydown Humpty", "ldHb", k=31, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(1/8), radius=40),
            imacmb.roll(r(0.5), line_length=110),
            imacmb.loop(-r(0.5), radius=40),
            imacmb.snap(r(1), line_length=110 + 2 * 40 ),
            imacmb.loop(r(1/8), radius=40)
        ]
    ),
    imacmb.create(ManInfo(
            "Shark Tooth", "Stoo", k=19, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(1/8), radius=40),
            imacmb.roll('2x4', line_length = 110 / c45 + 2 * 40),
            imacmb.loop(r(3/8), radius=40),
            imacmb.line(length=110),
            imacmb.loop(r(1/4), radius=40)
        ]
    ),
    imacmb.create(ManInfo(
            "Avalanche", "Av", k=21, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(0.5), radius=mps.loop_radius),
            imacmb.snap(r(1), padded=False),
            imacmb.loop(r(0.5), radius=mps.loop_radius),
        ], loop_radius=100
    ),
    imacmb.create(ManInfo(
            "Half Cuban", "Hc8", k=23, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.roll('2x2', padded=False),
            imacmb.loop(r(5/8)),
            imacmb.roll(r(0.5), line_length=100),
            imacmb.loop(r(1/8))
        ]
    ),
    imacmb.create(ManInfo(
            "Immelman", "Imm", k=19, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.roll('2x2', padded=False),
            imacmb.loop(r(1/2), radius=100),
            imacmb.roll(r(0.5), padded=False),
        ]
    ),
    imacmb.create(ManInfo(
            "Spin", "Spin", k=13, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.spin(r(-1.75)),
            imacmb.line(length = 125),
            imacmb.loop(r(1/4)),
        ]
    ),
    imacmb.create(ManInfo(
            "Humpty", "hB", k=16, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.CROSS, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM, Direction.DOWNWIND)
        ),[
            imacmb.loop(r(0.25)),
            imacmb.line(),
            imacmb.loop(r(1/2)),
            imacmb.roll('2x8'),
            imacmb.loop(r(1/4))
        ]
    ),
    imacmb.create(ManInfo(
            "Teardrop", "TD", k=26, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(1/8)),
            imacmb.roll(r(1), line_length=100/c45),
            imacmb.loop(r(5/8)),
            imacmb.roll(r(1/2), line_length=100),
            imacmb.loop(r(1/4))
        ]
    ),
    imacmb.create(ManInfo(
            "StallTurn", "St", k=30, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(1/4)),
            imacmb.roll('2x4'),
            imacmb.stallturn(),
            imacmb.roll(r(1/2)),
            imacmb.loop(r(1/4)),
        ]
    ),
    imacmb.create(ManInfo(
            "Q Loop", "qlp", k=25, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(1/4)),
            imacmb.line(),
            imacmb.loop(r(3/4), rolls=1, rollangle=r(1/4)),
            imacmb.roll('2x4', padded=False),
        ]
    ),
])


if __name__ == "__main__":

 
    sdef.plot().show()
#    import os
#    sdef.create_fcjs('imac_unlimited_2024', f'{os.environ['HOME']}/Desktop/templates', 'IMAC')
#    sdef.to_json("flightanalysis/data/IMAC_Sportsman2024_schedule.json")