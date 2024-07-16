"""This file defines a Intermediate24 sequence using the ManDef Classes and helper functions."""

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
        ], loop_radius = 27, line_length=150),

    f3amb.create(ManInfo("inv half square", "hSql", 2, Position.END,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(r(1/4)),
            f3amb.line(),
            f3amb.loop(r(1/4))
        ]),

    f3amb.create(ManInfo(
            "2HorzRolls", "2hzrolls", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
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
        ], loop_radius = 40,line_length=80),

   f3amb.create(ManInfo(
            "Square on Corner", "sqLc", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
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
        ], loop_radius = 30, line_length=70),

    f3amb.create(ManInfo("Stall Turn", "stall", 3,Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.roll([np.pi*2]),
            f3amb.stallturn(),
            f3amb.line(),
            f3amb.loop(np.pi/2) 
        ], loop_radius = 30),

    f3amb.create(ManInfo(
            "Double Immelman", "dimmel", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi),
            f3amb.roll("1/2", padded=False),
            f3amb.line(length=98),
#            f3amb.roll("roll_option[1]", padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll("1/2", padded=False),
        ], loop_radius=80), 

    f3amb.create(ManInfo("Humpty Bump", "humpty", 3, Position.END,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi*2/2),
            f3amb.line(),
            f3amb.loop(np.pi*2/4),
        ],loop_radius = 30),

    f3amb.create(ManInfo(
            "2Loops", "loops", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(4*np.pi),
        ],loop_radius = 80),

    f3amb.create(ManInfo(
            "1/2Square on Corner", "hsc", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.line(),
            f3amb.loop(np.pi/2),
            f3amb.line(),
            f3amb.loop(np.pi/4),
        ], loop_radius = 30, line_length=50),

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
        loop_radius=60, line_length=120
        ),

    f3amb.create(ManInfo("Figure 6", "fig6", 2, Position.END,
            BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2*3/4),
            f3amb.line(length=60),
            f3amb.loop(-np.pi*2/4),
         ], loop_radius = 40),

    f3amb.create(ManInfo("Vert Dwl", "vertdl", 2, Position.CENTRE,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi*0.5),
            f3amb.line(),
            f3amb.loop(np.pi*0.5),
        ], loop_radius = 35),

    f3amb.create(ManInfo("Top Hat", "tophat", 2, Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi*2/4),
            f3amb.roll([np.pi]), 
            f3amb.loop(np.pi*2/4),
            f3amb.line(length=38),
            f3amb.loop(np.pi*2/4),
            f3amb.line(),
            f3amb.loop(np.pi*2/4),
        ], loop_radius = 30),

    f3amb.create(ManInfo("Figure Z", "figz", 2, Position.CENTRE,
            BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2*3/8),
            f3amb.line(c45), 
            f3amb.loop(-np.pi*2*3/8),
        ], loop_radius = 20),

   f3amb.create(ManInfo("Split S", "splits", 2, Position.END,
            BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.roll("1/2", padded=False), 
            f3amb.loop(np.pi*2/2),
        ], loop_radius = 80),

  f3amb.create(ManInfo("Upline 45", "upl45", 2, Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi*2/8),  
            centred(f3amb.roll([2*np.pi])), 
            f3amb.loop(-np.pi*2/8),  
        ], loop_radius = 45),


])

if __name__ == "__main__":

    Intm24FC_def.plot().show()

###    Intm24FC_def.to_json('C:/Users/coach/OneDrive/Desktop/Templates/test4/flightanalysis/data/Interm24FC.json')
#    Intm24FC_def.to_json('Intm24FC-fcj-LR.json')
#    Intm24FC_def.create_fcj('intermediate', 'Intm24FC-fcj-LR-template.json', 1)
###    from flightplotting.plots import plotsec

###    Intm24FC, template = Intm24FC_def.create_template(170, 1)
###    #from plots import plotsec
    
###    plotsec(template).show()
