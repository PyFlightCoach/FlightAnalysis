"""This file defines a P23 sequence using the ManDef Classes and helper functions."""
from flightanalysis import (
    SchedDef, ManInfo, BoxLocation, Position, Orientation, 
    Height, Direction, MBTags, f3amb, centred, r, ManParm,
    Combination, c45
)
from flightanalysis.scoring.f3a_downgrades import DGGrps
import numpy as np


p23_def = SchedDef([
    f3amb.create(ManInfo(
            "Top Hat", "tHat", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/2), 
            centred(f3amb.roll("1/2",line_length=100)),
            f3amb.loop(-np.pi/2),
            f3amb.roll("2x4"),
            f3amb.loop(-np.pi/2)
        ]),
    f3amb.create(ManInfo("Half Square Loop", "hSqL", 2, Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2)
        ]),
    f3amb.create(ManInfo("Humpty Bump", "hB", 4, Position.CENTRE,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi/2),
            f3amb.roll("1/1"), # TODO this should change to 1 sometime
            centred(f3amb.loop(np.pi)),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/2),
            MBTags.CENTRE,
        ]),
    f3amb.create(ManInfo("Half Square on Corner", "hSqLC", 3, Position.END,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/4),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/4)
        ], line_length=130*c45),
    f3amb.create(ManInfo("45 Upline Snaps", "upL", 5, Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi/4),
            centred(f3amb.snap(r(1.5))),
            f3amb.loop(-np.pi/4) 
        ], line_length=110 + 130/c45),
    f3amb.create(ManInfo("Half 8 Sided Loop", "h8L", 3, Position.END,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/4),
            f3amb.line(),
            f3amb.loop(-np.pi/4),
            f3amb.line(),
            f3amb.loop(-np.pi/4),
            f3amb.line(),
            f3amb.loop(-np.pi/4)            
        ], line_length=50),
    f3amb.create(ManInfo("Roll Combo", "rollC", 4, Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        ),[
            centred(f3amb.roll([np.pi, np.pi, -np.pi, -np.pi], padded=False))
        ]),
    f3amb.create(ManInfo("Immelman Turn", "pImm", 2, Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi),
            f3amb.roll("1/2", padded=False)
        ],loop_radius=100),
    f3amb.create(ManInfo("Inverted Spin",  "iSp",  4, Position.CENTRE,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        ),[
            0,
            f3amb.spin(r(2.5)),
            f3amb.line(speed=25),
            f3amb.loop(np.pi/2)
        ]),
    f3amb.create(
        ManInfo("Humpty Bump",  "hB2",  3, Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),
        [
            f3amb.loop(np.pi/2),
            f3amb.roll("roll_option[0]"),
            f3amb.loop(np.pi),
            f3amb.roll("roll_option[1]"),
            f3amb.loop(-np.pi/2)   
        ], 
        roll_option=ManParm(
            "roll_option", 
            Combination(desired=[
                [np.pi, np.pi],
                [np.pi, -np.pi],
                [-np.pi, np.pi],
                [-np.pi, -np.pi],
                [np.pi*1.5, -np.pi/2], 
                [-np.pi*1.5, np.pi/2]
            ]),
            0
        )
    ),
    f3amb.create(ManInfo("Reverese Figure Et",  "rEt",  4, Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi/4),
            f3amb.roll([np.pi, -np.pi], line_length=str(2*f3amb.mps.loop_radius)),
            f3amb.loop(7*np.pi/4),
            MBTags.CENTRE,
            f3amb.roll("2x4", line_length=100),
            f3amb.loop(-np.pi/2)
        ], 
        loop_radius=70
    ),
    f3amb.create(ManInfo("Half Square Loop", "sqL", 2,Position.END,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2)
        ]),
    f3amb.create(ManInfo("Figure M", "M", 5,Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("roll_option[0]", speed=30),
            MBTags.CENTRE,
            f3amb.stallturn(),
            f3amb.line(speed=30),
            f3amb.loop(-np.pi),
            f3amb.line(speed=30),
            f3amb.stallturn(),
            f3amb.roll("roll_option[1]", speed=30),
            f3amb.loop(np.pi/2)
        ],
        roll_option=ManParm(
            "roll_option", 
            Combination(desired=[
                [np.pi*3/2, np.pi*3/2],
                [-np.pi*3/2, -np.pi*3/2],
            ]),
            1
        ),
        line_length=150.0
    ),
    f3amb.create(ManInfo("Fighter Turn", "fTrn", 4,Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("roll_option[0]"),
            f3amb.loop(-np.pi),
            f3amb.roll("roll_option[1]"),
            f3amb.loop(np.pi/4)
        ],
        roll_option=ManParm("roll_option", Combination(
            desired=[
                [-np.pi/2, np.pi/2],
                [np.pi/2, -np.pi/2]
            ]
        ),0)),
    f3amb.create(ManInfo("Triangular Loop", "trgle", 3,Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            centred(f3amb.roll("1/2", padded=False)),
            f3amb.line(length=str(f3amb.mps.line_length*c45-0.5*np.pi*30/f3amb.mps.partial_roll_rate)),
            f3amb.loop(-np.pi*3/4),
            f3amb.roll("2x4"),
            centred(f3amb.loop(np.pi/2)),
            f3amb.roll("2x4"),
            f3amb.loop(-np.pi*3/4),
            f3amb.line(length=str(f3amb.mps.line_length*c45-0.5*np.pi*30/f3amb.mps.partial_roll_rate)),
            centred(f3amb.roll("1/2", padded=False))
        ]),
    f3amb.create(ManInfo("Shark Fin", "sFin", 3,Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2", line_length=80),
            f3amb.loop(-np.pi*3/4),
            f3amb.roll("2X4", line_length=80/c45 + 60), #ll / c45 + 2*r
            f3amb.loop(-np.pi/4),
        ],loop_radius=30),
    f3amb.create(ManInfo("Loop", "loop", 3,Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        ),[
            0,
            f3amb.loop(-np.pi*3/4),
            centred(f3amb.loop(-np.pi/2,rolls="roll_option")),
            f3amb.loop(np.pi*3/4),
            0
        ],
        loop_radius=80,
        roll_option=ManParm(
            "roll_option", 
            Combination(desired=[[np.pi], [-np.pi]]), 0
        ))
])


p23_def.iSp.eds.e_1.dgs = DGGrps.sp_line_accel
p23_def.M.eds.e_1_pad2.dgs = DGGrps.st_line_decel
p23_def.M.eds.e_3.dgs = DGGrps.st_line_accel
p23_def.M.eds.e_5.dgs = DGGrps.st_line_decel
p23_def.M.eds.e_7_pad1.dgs = DGGrps.st_line_accel

if __name__ == "__main__":
    
 #   p23_def.plot().show()
#    p23_def.create_fcj('P23', 'p23_template_fcj.json')
    p23_def.to_json("flightanalysis/data/f3a_p23_schedule.json")
   # import os
   # p23_def.create_fcjs('p23', f'{os.environ['HOME']}/Desktop/templates/')