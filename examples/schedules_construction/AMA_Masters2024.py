"""This file defines a AMA Masters 2024 sequence using PyFligthCoach ManDef Classes and helper functions.
   Author Angel Espinosa.
"""

from flightanalysis.definition import *
from flightanalysis.elements import *
from flightanalysis.scoring.criteria import *
import numpy as np

c45 = np.cos(np.radians(45))

Mast24FC_def = SchedDef([

#####################################
    f3amb.create(ManInfo(
            "Triang-1/4rolls", "trgle-1/4rolls", 3,Position.CENTRE,
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.MID)
        ),[
            MBTags.CENTRE,
            f3amb.loop(r(1/8)),
            centred(f3amb.roll('2x4', padded=True)), 
            f3amb.loop(r(-3/8)),
            centred(f3amb.roll(np.pi*2,line_length=2*107,padded=True)), 
            f3amb.loop(r(-3/8)),
            centred(f3amb.roll('2x4', padded=True)),
            f3amb.loop(r(1/8)),
            MBTags.CENTRE,
        ], line_length=150),

#####################################
    f3amb.create(ManInfo(
            "half square-roll", "hSl-roll", 2, Position.END,
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(r(1/4)),
            centred(f3amb.roll(np.pi*2,line_length=2*55,padded=True)),
            f3amb.loop(r(1/4)),
        ]),

#####################################
    f3amb.create(ManInfo(
            "SLC-Rolls", "slc-rolls", 5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
           MBTags.CENTRE,
            f3amb.loop(r(1/8)),
            centred(f3amb.roll(np.pi,line_length=2*40,padded=True)),
            f3amb.loop(-r(1/4)),
            centred(f3amb.roll(np.pi,line_length=2*40,padded=True)),
            f3amb.loop(r(1/4)),
            centred(f3amb.roll(np.pi,line_length=2*40,padded=True)),
            f3amb.loop(-r(1/4)),
            centred(f3amb.roll(np.pi,line_length=2*40,padded=True)),
            f3amb.loop(r(1/8)),
            MBTags.CENTRE, 
        ], line_length=80),

#####################################
    f3amb.create(ManInfo(
            "Figure 9-roll", "fig9-roll", 3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(r(1/4)),
            centred(f3amb.roll(np.pi,line_length=2*60,padded=True)),
            f3amb.loop(r(3/4)), 
        ], loop_radius = 40),

#####################################
    f3amb.create(ManInfo(
            "Roll Combo", "RollC", 4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            centred(f3amb.roll(r([0.25, 0.25, 0.25, -0.25, -0.25, -0.25]), padded=False)), 
        ]) ,

#####################################
    f3amb.create(ManInfo(
            "Stall Turn", "stall", 3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(r(1/4)),
            f3amb.line(length=60),
            f3amb.stallturn(),
            centred(f3amb.roll([np.pi],line_length=150,padded=True)),
            f3amb.loop(-r(1/4)),
        ]),

#####################################
    f3amb.create(ManInfo(
            "Double Immelman", "dimmel", 4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[ 
            f3amb.roll(np.pi*2, padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll(np.pi*2*1/4, padded=False),
            f3amb.line(length=90),
            f3amb.roll(-np.pi*2*1/4, padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll(np.pi, padded=False),
            f3amb.line(length=180),
        ], loop_radius=90), 

#####################################
    f3amb.create(ManInfo(
            "Humpty 1/2rolls", "humpty", 3, Position.END,
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            centred(f3amb.roll(r([0.5, -0.5]), padded=False)), 
            f3amb.loop(-np.pi*2/2),
            centred(f3amb.roll([np.pi*2/2], line_length=155,padded=True)), 
            f3amb.loop(np.pi*2/4),
        ],loop_radius=30),

#####################################
    f3amb.create(ManInfo(
            "Loop-intgrolls ", "loopRlls", 5, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(r(1), rolls=[r(0.5), -r(0.5)], rollangle=r(0.5)),
        ],loop_radius=100),

#####################################
    f3amb.create(ManInfo(
            "1/2SquareCorner-Rolls", "hscRolls", 2, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/8),
            centred(f3amb.roll(np.pi*2/2, padded=True)),
            f3amb.loop(-np.pi*2/4),
            centred(f3amb.roll(np.pi*2/2, padded=True)),
            f3amb.loop(np.pi*2/8),

        ], loop_radius = 30,line_length=100),
#####################################
    f3amb.create(ManInfo(
            " 1/2 Cloverleaf-rolls", "hClovRolls", 5, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/4),
            MBTags.CENTRE,
            f3amb.roll(np.pi*2/2, padded=True),           
            f3amb.loop(-np.pi*2*3/4), 
            f3amb.roll(np.pi*2/2, padded=True),
            f3amb.loop(np.pi*2*3/4),
            f3amb.roll(np.pi*2/2, padded=True),
            MBTags.CENTRE,
            f3amb.loop(-np.pi*2/4),           
        ], loop_radius = 50,line_length=100),

#####################################
    f3amb.create(ManInfo(
            "Rev Fig Et-Rolls", "rEtRolls", 4, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi*2/8),
            f3amb.roll(np.pi*2/2, padded=True),  
            f3amb.loop(np.pi*2*5/8),
            centred(f3amb.roll(r([0.25, 0.25]), padded=True)),
           f3amb.loop(np.pi*2/4),
        ], loop_radius = 45,line_length=85),
#####################################
    f3amb.create(ManInfo(
            "Spin2", "2Spin", 3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM),
        ),[      
            MBTags.CENTRE,
            f3amb.spin(r(2)), 
            f3amb.roll(np.pi*2/2, padded=True),
            f3amb.loop(np.pi*2/4),            
        ], loop_radius = 30, line_length=95),
#####################################
    f3amb.create(ManInfo(
            "Top Hat", "tophat", 3, Position.END,
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/4),
            centred(f3amb.roll(r([0.25, 0.25]), padded=True)),
            f3amb.loop(np.pi*2/4),
            f3amb.line(),
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=100),
            f3amb.loop(np.pi*2/4),
        ], loop_radius = 30,line_length=85),
#####################################
    f3amb.create(ManInfo(
            "Fig Z -snap", "figzSnap", 4, Position.CENTRE,
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2*3/8),
            centred(f3amb.snap(r(1))),            
            f3amb.loop(-np.pi*2*3/8),
        ], loop_radius = 20,line_length=90),
#####################################
    f3amb.create(ManInfo(
            "Comet-Rolls", "ComRolls", 3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi*2/8), 
            centred(f3amb.roll(r([0.25, 0.25]), padded=True)),           
            f3amb.loop(-np.pi*2*3/4),  
            centred(f3amb.roll(np.pi*2, padded=True)),          
            f3amb.loop(np.pi*2/8), 
        ], loop_radius=45,line_length=100),
#####################################
    f3amb.create(ManInfo(
            "Figure S-roll", "figSRoll", 5, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            MBTags.CENTRE,
            f3amb.loop(r(3/8)),
            f3amb.loop(r(1/8), rolls="rke_opt[0]"),
            MBTags.CENTRE,
            f3amb.loop("rke_opt[1]", ke=True),
            f3amb.loop("rke_opt[2]", ke=True, rolls="rke_opt[3]"),
            MBTags.CENTRE
        ], 
            rke_opt=ManParm("rke_opt", 
            Combination(desired=r([
                [1/4, 3/8, 1/8, 1/4], 
                [-1/4, -3/8, -1/8, -1/4]
        ])), 0),loop_radius=35),

])

if __name__ == "__main__":

    import os
##    Mast24FC_def.plot().show()

    Mast24FC_def.create_fcjs('AMA_Masters2024', f'{os.environ['HOME']}/Desktop/templates/')



