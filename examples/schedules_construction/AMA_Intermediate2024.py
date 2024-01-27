"""This file defines a AMA Intermediate 2024 sequence using PyFligthCoach ManDef Classes and helper functions.
   Author Angel Espinosa with help from Thomas David
"""

from flightanalysis.definition import *
from flightanalysis.elements import *
from flightanalysis.scoring.criteria import *
import numpy as np

c45 = np.cos(np.radians(45))

Intm24FC_def = SchedDef([

    f3amb.create(ManInfo("InvTriang", "trgle", 5,Position.CENTRE,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.MID)
        ),[
            MBTags.CENTRE,
            f3amb.loop(r(1/8)),
            f3amb.line(),
            f3amb.loop(r(3/8)),
            f3amb.line(length=215), 
            f3amb.loop(r(3/8)),
            f3amb.line(),
            f3amb.loop(r(1/8)),
            MBTags.CENTRE,
        ], loop_radius=40, line_length=150),

    f3amb.create(ManInfo("inv half square", "hSql", 2, Position.END,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.MID)
        ),[
            f3amb.loop(r(1/4)),
            f3amb.line(length=105),
            f3amb.loop(r(1/4)),
        ], loop_radius=50),

    f3amb.create(ManInfo("2HorzRolls", "hzrolls", 4, Position.CENTRE, 
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.roll(r(2), padded=False)
        ]),

    f3amb.create(ManInfo("half cuban", "hcuban", 2, Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(r(5/8)),
            f3amb.roll(r(1/2)), 
            f3amb.loop(r(1/8)),
        ], loop_radius = 65,line_length=155),

   f3amb.create(ManInfo("Square on Corner", "sqLc", 4, Position.CENTRE, 
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            MBTags.CENTRE,
            f3amb.loop(r(1/8)),
            f3amb.line(),
            f3amb.loop(r(1/4)),
            f3amb.line(),
            centred(f3amb.loop(r(1/4))),
           f3amb.line(),
            f3amb.loop(r(1/4)),
            f3amb.line(),
            f3amb.loop(r(1/8)),
            MBTags.CENTRE, 
        ], line_length=80),

    f3amb.create(ManInfo("Stall Turn", "stall", 3,Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.roll([np.pi*2],line_length=150),
            f3amb.stallturn(),
            f3amb.line(length=160),
            f3amb.loop(np.pi/2), 
        ], loop_radius = 45),

    f3amb.create(ManInfo("Double Immelman", "dImm", 4, Position.CENTRE, 
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi),
            f3amb.roll("1/2", padded=False),
            f3amb.line(length=100),
            f3amb.loop(-np.pi),
            f3amb.roll("1/2", padded=False),
        ], loop_radius=100), 

    f3amb.create(ManInfo("Humpty Bump", "hB", 3, Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi*2/2),
            f3amb.line(),
            f3amb.loop(np.pi*2/4),
        ],loop_radius = 45,line_length=120),

    f3amb.create(ManInfo("2Loops", "loops", 3, Position.CENTRE, 
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(4*np.pi),
        ],loop_radius = 110),

    f3amb.create(ManInfo("Half Square on Corner", "hSqL2", 4, Position.END, 
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.MID)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.line(),
            f3amb.loop(np.pi/2),
            f3amb.line(),
            f3amb.loop(np.pi/4),
        ], line_length=80, loop_radius=40),


    f3amb.create(ManInfo("Cuban Eight", "cuban", 2, Position.CENTRE,
            BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.MID)
        ),[

            f3amb.loop(5*np.pi/4),            
            centred(f3amb.roll(np.pi)),                       
            f3amb.loop(3*np.pi/2), 
            centred(f3amb.roll(np.pi)),
            f3amb.loop(np.pi/4),   
        ],
        loop_radius=75, line_length=150
        ),

    f3amb.create(ManInfo("Figure 6", "fig6", 2, Position.END,
            BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2*3/4),
            f3amb.line(length=40),
            f3amb.loop(-np.pi*2/4),
         ], loop_radius = 50),

    f3amb.create(ManInfo("Vert Dwl", "vertdl", 2, Position.CENTRE,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi*0.5),
            f3amb.line(length=125),
            f3amb.loop(np.pi*0.5),
        ]),

    f3amb.create(ManInfo("Top Hat", "tHat", 2, Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.roll([np.pi]), 
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=30),
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=110),
            f3amb.loop(np.pi*2/4),
        ], loop_radius = 45),

    f3amb.create(ManInfo("Figure Z", "Z", 2, Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2*3/8),
            f3amb.line(c45), 
            f3amb.loop(-np.pi*2*3/8),
        ], loop_radius =35, line_length=130),

   f3amb.create(ManInfo("Split S", "splitS", 2, Position.END,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.roll("1/2", padded=False), 
            f3amb.loop(np.pi*2/2),
        ], loop_radius = 75),

   f3amb.create(ManInfo("Upline 45", "upl45", 2, Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/8),  
            centred(f3amb.roll([2*np.pi])), 
            f3amb.loop(-np.pi*2/8),  
        ]),

])

if __name__ == "__main__":
    import os
    #Intm24FC_def.plot().show()

    Intm24FC_def.create_fcjs('AMA_Intermediate2024', f'{os.environ['HOME']}/Desktop/templates/')

