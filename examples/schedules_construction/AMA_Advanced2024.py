"""This file defines a AMA Advanced 2024 sequence using PyFligthCoach ManDef Classes and helper functions.
   Author Angel Espinosa with help from Thomas David.
"""

from flightanalysis.definition import *
from flightanalysis.elements import *
from flightanalysis.scoring.criteria import *
import numpy as np

c45 = np.cos(np.radians(45))

Adv24FC_def = SchedDef([

    f3amb.create(ManInfo("Triang-roll", "trgle-roll", 3,Position.CENTRE,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.MID)
        ),[
            MBTags.CENTRE,
            f3amb.loop(r(-1/8)),
            f3amb.line(),
            f3amb.loop(r(-3/8)), 
            centred(f3amb.roll(np.pi*2,line_length=2*107,padded=True)), 
            f3amb.loop(-r(3/8)),
            f3amb.line(),
            f3amb.loop(-r(1/8)),
            MBTags.CENTRE,
        ], line_length=150),

    f3amb.create(ManInfo("half square-roll", "hSl-roll", 2, Position.END,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.MID)
        ),[
            f3amb.loop(-r(1/4)),
            centred(f3amb.roll(np.pi,line_length=2*55,padded=True)),
#            centred(f3amb.roll(np.pi,padded=True)),
            f3amb.loop(r(1/4)),
        ]),

    f3amb.create(ManInfo(
            "SLC-Rolls", "slc-rolls", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
           MBTags.CENTRE,
            f3amb.loop(r(1/8)),
            f3amb.line(),
            f3amb.loop(r(1/4)),
            centred(f3amb.roll(np.pi,line_length=2*40,padded=True)),
            f3amb.loop(-r(1/4)),
            centred(f3amb.roll(np.pi,line_length=2*40,padded=True)),
            f3amb.loop(r(1/4)),
            f3amb.line(),
            f3amb.loop(r(1/8)),
            MBTags.CENTRE, 
#        ], loop_radius = 30, line_length=80),
        ], line_length=80),

    f3amb.create(ManInfo(
            "Figure 9", "fig9", k=3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(np.pi*2/4),
            centred(f3amb.roll(np.pi,line_length=2*60,padded=True)),
            f3amb.loop(np.pi*2*3/4),
            f3amb.line(length = 100), 
        ], loop_radius = 40),

    f3amb.create(ManInfo(
            "1/4 Rolls", "1/4Rolls", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            centred(f3amb.roll('4x4', padded=False)),  
        ]) ,

    f3amb.create(ManInfo(
            "Stall Turn", "stall", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=65),
            f3amb.stallturn(),
            centred(f3amb.roll([np.pi],line_length=150,padded=True)),
#            f3amb.line(length=65),
            f3amb.loop(-np.pi/2) 
        ]),

    f3amb.create(ManInfo(
            "Double Immelman", "dimmel", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.line(length = 20), 
            f3amb.roll(np.pi, padded=False),
            f3amb.loop(np.pi),
            f3amb.roll(np.pi, padded=False),
            f3amb.line(length=98),
            f3amb.loop(-np.pi),
            f3amb.roll(np.pi, padded=False),
            f3amb.line(length=170),
        ], loop_radius=90), 

    f3amb.create(ManInfo("Humpty 1/2roll", "humpty", 2, Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.line(), 
            f3amb.loop(-np.pi*2/2),
            centred(f3amb.roll([np.pi*2/2], line_length=140,padded=True)), 
            f3amb.loop(np.pi*2/4),
        ],loop_radius=30),

    f3amb.create(ManInfo(
            "roll loop roll ", "RloopR", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.roll(np.pi, line_length=2*50, padded=True), 
            centred(f3amb.loop(-np.pi*2)),
            f3amb.roll(np.pi, line_length=2*50, padded=True), 
        ],loop_radius = 100),

    f3amb.create(ManInfo(
            "1/2Square on Corner", "hsc", k=2, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/8),
            f3amb.line(),
            f3amb.loop(np.pi*2/4),
            f3amb.line(),
            f3amb.loop(np.pi*2/8),

        ], loop_radius = 30,line_length=65),

        f3amb.create(ManInfo(
            " 1/2 Cloverleaf", "hClov", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/4),
            MBTags.CENTRE,
            f3amb.line(length=75),            
            f3amb.loop(np.pi*2*3/4), 
            centred(f3amb.line(length=str(f3amb.mps.loop_radius * 2))),
            f3amb.loop(np.pi*2*3/4),
            MBTags.CENTRE,
            f3amb.line(length=75),
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=80),
        ], loop_radius = 50),


        f3amb.create(ManInfo(
            "Rev Fig Et", "rEt", k=3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/8),
            f3amb.line(length=70),
            f3amb.loop(np.pi*2*5/8),
            f3amb.line(length=90),
            f3amb.loop(-np.pi*2/4),
        ], loop_radius = 45),

        f3amb.create(ManInfo(
            "Spin2", "2Spin", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM),
        ),[      
            MBTags.CENTRE,
            f3amb.spin(r(2)), 
            f3amb.line(length=100),
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=90),            
        ], loop_radius = 30),

    f3amb.create(ManInfo("Top Hat", "tophat", 3, Position.END,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=15),
            f3amb.roll([np.pi], padded=False), 
            f3amb.line(length=15),
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=25),
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=95),
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=100),
        ], loop_radius = 30),

    f3amb.create(ManInfo("Fig Z roll", "figzR", 4, Position.CENTRE,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2*3/8),
            f3amb.line(length=30),
            centred(f3amb.roll([np.pi], padded=False)), 
            f3amb.line(length=30),
            f3amb.loop(np.pi*2*3/8),
            f3amb.line(length=90),
        ], loop_radius = 20),

        f3amb.create(ManInfo(
            "Comet", "Com", k=3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/8), 
            f3amb.line(length=115),           
            f3amb.loop(-np.pi*2*3/4), 
            f3amb.line(length=115),           
            f3amb.loop(np.pi*2/8),
            f3amb.line(length=50), 
        ], loop_radius=45),

        f3amb.create(ManInfo(
            "Figure S", "figS", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi),            
            MBTags.CENTRE,
            f3amb.loop(-np.pi),            
            MBTags.CENTRE,
            f3amb.line(length=40),
        ], loop_radius = 35 ),


])

if __name__ == "__main__":

    import os
##    Adv24FC_def.plot().show()


    Adv24FC_def.create_fcjs('AMA_Advanced2024', f'{os.environ['HOME']}/Desktop/templates/')


