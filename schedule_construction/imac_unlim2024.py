from flightanalysis import SchedDef, ManInfo, BoxLocation, Position, Orientation, Height, Direction, imacmb, r, ManParm, Combination
import numpy as np


c45 = np.cos(np.radians(45))


sdef = SchedDef([
    imacmb.create(ManInfo(
            "Q Loop", "qLoop", k=44, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.roll([r(1/8), r(1/8), -r(1.75)], rolltypes='rrs', padded=False),
            imacmb.loop(-2*np.pi*7/8),
            imacmb.roll('2x2'),
            imacmb.loop(-np.pi/4)
        ]),
    imacmb.create(ManInfo(
            "Stallturn", "sTurn", k=53, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(-r(1/4)),
            imacmb.roll([r(1/4), -r(1.25)], rolltypes='rs'),
            imacmb.stallturn(),
            imacmb.roll('2x4'),
            imacmb.loop(r(1/4)),
        ]),
    imacmb.create(ManInfo(
            "Rolling Circle", "rcirc", k=46, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop('directions[0]', ke=True, rolls='directions[1]', radius='loop_radius'),
            imacmb.loop('directions[2]', ke=True, rolls=0, radius='loop_radius'),
            imacmb.loop('directions[3]', ke=True, rolls='directions[4]', radius='loop_radius'),
        ], 
        directions=ManParm('directions', Combination(desired=[
            [r(0.49), -r(1), r(0.02), r(0.49), r(1)],
            [-r(0.49), r(1), -r(0.02), -r(0.49), -r(1)]
        ]), 1),
        loop_radius=100),
    imacmb.create(ManInfo(
                "Immelman", "Imm", k=39, position=Position.END, 
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT), 
                end=BoxLocation(Height.TOP)
            ),[
                imacmb.roll([r(3/4), -r(1/4), -r(1/4), -r(1/4)], padded=False),
                imacmb.loop(np.pi, radius=100),
                imacmb.snap(r(1.5), break_angle=np.radians(-15), padded=False),            
            ]
        ),
    imacmb.create(ManInfo(
            "Laydown Humpty", "lhb", k=49, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.TOP)
        ),[
            imacmb.loop(-3*np.pi/4, radius=40),
            imacmb.roll([r(1.75), -r(1/4)], rolltypes='sr', break_angle=np.radians(-15)),
            imacmb.loop(np.pi, radius=40),
            imacmb.roll('4x4'),
            imacmb.loop(r(1/8))
        ]
    ),
    imacmb.create(ManInfo(
            "Double Humpty", "dhb", k=68, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.spin('directions[0]'),
            imacmb.snap(r(-1), 'directions[1]'),
            imacmb.loop(np.pi),
            imacmb.snap(r(2)),
            imacmb.loop(np.pi),
            imacmb.roll('directions[2]'),
            imacmb.loop(np.pi/2)
        ],
        directions=ManParm('directions', Combination(desired=[
            [-r(1.75), r(1), r(1.75)],
            [r(1.75), -r(1), -r(1.75)]
        ]), 1),
        full_roll_rate=2*np.pi
    ),
    imacmb.create(ManInfo(
            "Loop", "Loop", k=2, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(1), rolls=[r(1/8), r(1/8), r(1.25)], rolltypes='rrs', radius=100, rollangle=r(1/8))  
        ],
    ),
    imacmb.create(ManInfo(
            "Sharks Tooth", "sTooth", k=45, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(-r(1/8)),
            imacmb.roll('4x8', line_length=110 / c45 + 2*50),
            imacmb.loop(r(-3/8)),
            imacmb.roll([r(1.25), r(-0.75)], rolltypes='rs', break_angle=-np.radians(15), line_length=110),
            imacmb.loop(r(1/4)),
        ], partial_roll_rate=np.pi/2, full_roll_rate=1.5*np.pi
    ),
    imacmb.create(ManInfo(
            "Teardrop", "TD", k=49, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(r(1/8)),
            imacmb.roll('3x2', line_length=130 / c45),
            imacmb.loop(r(-5/8)),
            imacmb.roll([r(1/4), r(1/4), r(1)], rolltypes='rrs', line_length=130, break_angle=-np.radians(15)),
            imacmb.loop(r(1/4)),
        ]),
    imacmb.create(ManInfo(
            "Half Cuban", "hcu", k=41, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.snap(r(1.5), padded=False),
            imacmb.loop(-r(5/8), radius=75),
            imacmb.roll([r(1/4), r(1/4), -r(1)], line_length=150),
            imacmb.loop(-r(1/8), radius=75)
        ], loop_radius=75, partial_roll_rate=np.pi*1.25, full_roll_rate=np.pi*1.25, point_length=10)
    
])



if __name__ == "__main__":

 
    sdef.plot().show()
#    import os
#    sdef.create_fcjs('imac_unlimited_2024', f'{os.environ['HOME']}/Desktop/templates', 'IMAC')
#    sdef.to_json("flightanalysis/data/IMAC_Unlimited2024_schedule.json")