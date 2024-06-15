'''Author Vince Beesley 18/11/2023'''

from flightanalysis import *
import numpy as np

c45 = np.cos(np.radians(45))

a25_def = SchedDef([
     f3amb.create(ManInfo
        (
            "Triangle", "trgle", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(-np.pi/4),
            f3amb.line(),          
            f3amb.loop(-np.pi*3/4), 
            centred(f3amb.roll(2*np.pi, line_length=str(2 * c45 * f3amb.mps.line_length))),
            f3amb.loop(-np.pi*3/4),
            f3amb.line(),
            f3amb.loop(-np.pi/4),
            MBTags.CENTRE
        ],line_length=150),

     
    f3amb.create(ManInfo(
            "half square", "hSqL", k=2, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll(np.pi),
            f3amb.loop(np.pi/2)]),    
        

    f3amb.create(
        ManInfo(
            "Square on Corner", "sqL", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
                ),
        [
            MBTags.CENTRE,
            f3amb.loop(np.pi/4),
            f3amb.line(),
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"), 
            centred(f3amb.loop(-np.pi/2)),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi/2),
            f3amb.line(), 
            f3amb.loop(np.pi/4),
            MBTags.CENTRE], 
            line_length=80),
        

        f3amb.create(ManInfo(
            "Figure P", "fig9", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi*3/2)]),

        f3amb.create(ManInfo(
            "4 Quarter Rolls", "rollC", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
           centred(f3amb.roll('4x4', padded=False)),         
          ]),
            
            f3amb.create(ManInfo(
            "Stall Turn", "stall", k=3, position=Position.END, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.line(length=50),
            f3amb.stallturn(),
            f3amb.roll("1/2", line_length=180),
            f3amb.loop(-np.pi/2)]),
 
        f3amb.create(ManInfo(
            "Double Immelman", "dImm", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)            
        ),[
            f3amb.roll("1/2", padded=False),
            f3amb.loop(np.pi),
            f3amb.roll("1/2" , padded=False),            
            f3amb.line(length=80),
            f3amb.loop(-np.pi),
            f3amb.roll("1/2" , padded=False),
           ], 
            loop_radius=100),


        f3amb.create(ManInfo(
            "Humpty", "hB", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2), 
            f3amb.line(),           
            f3amb.loop(-np.pi),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2)]),

        
        f3amb.create(ManInfo(
            "Outside Loop", "loop", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[        
            f3amb.roll("1/2", padded=False),
            f3amb.line(length='ee_pause'),
            MBTags.CENTRE,
            f3amb.loop(-2*np.pi),
            MBTags.CENTRE,
            f3amb.line(length='ee_pause'),  
            f3amb.roll("1/2", padded=False),            
        ],
        loop_radius=100,
        
        ),

        f3amb.create(ManInfo(
            "Half Square on Corner", "hSqL2", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.line(),                      
            f3amb.loop(np.pi/2),             
            f3amb.line(),
            f3amb.loop(np.pi/4),
        ], line_length=130*c45),


        f3amb.create(ManInfo(
            "Cloverleaf", "hClov", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/2),
            MBTags.CENTRE,
            f3amb.line(),            
            f3amb.loop(3*np.pi/2), 
            centred(f3amb.line(length=str(f3amb.mps.loop_radius * 2))),
            f3amb.loop(np.pi*3/2),
            MBTags.CENTRE,
            f3amb.line(),
            f3amb.loop(np.pi/2),
        ]),

        f3amb.create(ManInfo(
            "Figure Et", "rEt", k=4, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.line(length=str(f3amb.mps.line_length / c45)),
            f3amb.loop(np.pi*5/4),
            f3amb.line(),
            f3amb.loop(-np.pi/2),
        ]),

        f3amb.create(ManInfo(
            "Spin", "iSpin", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM),
        ),[       
            MBTags.CENTRE,
            f3amb.spin(r(2)),  
            f3amb.line(length=165),
            f3amb.loop(np.pi/2),
            
        ]),


        f3amb.create(ManInfo(
            "Top Hat", "tHat", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2),
            f3amb.line(length=50),
            f3amb.loop(np.pi/2),
            f3amb.line(),
            f3amb.loop(np.pi/2)
        ]),

        f3amb.create(ManInfo(
            "Figure Z", "Z", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(3*np.pi/4),
            centred(f3amb.roll(np.pi)),       
            f3amb.loop(3*np.pi/4),
            ], loop_radius=40, 
            ),

        f3amb.create(ManInfo(
            "Comet", "Com", k=3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/4), 
            f3amb.line(),           
            f3amb.loop(-3*np.pi/2), 
            f3amb.line(),           
            f3amb.loop(np.pi/4),
        ], line_length=(1/c45 + 1) * 50 + 30 - (1/c45 - 2) * 50, loop_radius=50), 
 
        f3amb.create(ManInfo(
            "Figure S", "figS", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi),            
            MBTags.CENTRE,
            f3amb.loop(-np.pi),            
            MBTags.CENTRE,
        ], )

    ]  
)
 

if __name__ == "__main__":
    
#    a25_def.plot().show()

#    for mdef in a25_def:
#        mdef.plot(depth=170, wind=1).show()
 #   import os
 #   a25_def.create_fcjs('a25', f'{os.environ['HOME']}/Desktop/templates/')

    a25_def.to_json("flightanalysis/data/f3a_a25_schedule.json")

