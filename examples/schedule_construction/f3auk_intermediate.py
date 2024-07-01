'''
UKF3A Intermediate Template
Author Vince Beesley
'''
from flightanalysis import *
import numpy as np



c45 = np.cos(np.radians(45))

intermediate_def = SchedDef([  
   
    f3amb.create(ManInfo
        (
            "Turn Round", "trnround", k=0, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[  
            f3amb.loop(np.pi/4),
            f3amb.roll(np.pi, line_length = 2*65),
            f3amb.loop(5*np.pi/4),     
        ],
        loop_radius=65),    
    
    f3amb.create(ManInfo("Triangle", "trgle", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),
        [            
            f3amb.loop(np.pi*3/4),
            f3amb.line(c45),            
            centred(f3amb.loop(np.pi/2)),
            f3amb.line(-c45), 
            f3amb.loop(np.pi*3/4),
        ],line_length=150),
    
    f3amb.create(ManInfo
        (
            "Stall Turn", "stall", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[  
            f3amb.loop(np.pi/2),
            centred(f3amb.roll(2*np.pi)),      
            f3amb.stallturn(),
            f3amb.line(), 
            f3amb.loop(np.pi/2)
        ],line_length=200
        ),  
       

     f3amb.create(ManInfo(
            "4 Point Roll", "4pRoll", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
           centred(f3amb.roll('4x4', padded=False)),
        ],),       

     f3amb.create(ManInfo
        (
            "Immelman Turn", "immel", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[  
            f3amb.loop(np.pi),
            f3amb.roll(np.pi, padded=False),     
        ],loop_radius = 125,
        ),
        
    f3amb.create(ManInfo(
            "Square Loop", "sqrl", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)            
        ),
        [   
            f3amb.loop(-np.pi/2),            
            f3amb.line(roll=np.pi),
            f3amb.loop(np.pi/2), 
            centred(f3amb.line()),
            f3amb.loop(np.pi/2), 
            f3amb.line(roll=np.pi),       
            f3amb.loop(-np.pi/2),                               
           ], line_length = 100
        ),

    f3amb.create(ManInfo(
            "Split S", "splitS", k=2, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),
        [   f3amb.roll(2*np.pi, padded=False),         
            f3amb.loop(-np.pi),                    
        ],loop_radius = 125,
        ),

   f3amb.create(ManInfo(
            "Cuban Eight", "cuban", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[  
            f3amb.loop(-5*np.pi/4),            
            centred(f3amb.roll(np.pi)),                       
            f3amb.loop(-3*np.pi/2), 
            centred(f3amb.roll(np.pi)),
            f3amb.loop(-np.pi/4),          
        ],
        loop_radius=100, line_length=200
        ),

    f3amb.create(ManInfo(
            "Humpty Bump", "humpty", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),
        [
            f3amb.loop(-np.pi/2),
            f3amb.line(),             
            f3amb.loop(np.pi),
            f3amb.line(),
            f3amb.loop(np.pi/2),
        ]),

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
        ], 
        ),

     f3amb.create(ManInfo(
            "Figure 6", "fig6", k=3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            
            f3amb.loop(-np.pi/2),
            f3amb.roll(np.pi),
            f3amb.loop(-3*np.pi/2),
                    
           ]),

    f3amb.create(ManInfo
        (
            "Knife Edge", "knife", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),
        [  
            f3amb.roll(np.pi/2, padded=False),
            centred(f3amb.line(length=100)),
            f3amb.roll(np.pi/2, padded=False),
        ],         
        ),
        
     f3amb.create(ManInfo
        (
            " Half Outside Loop", "outloop", k=1, position=Position.END, 
            start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),            
            [  
            f3amb.loop(-np.pi),        
            ], loop_radius = 75,
        ),

    f3amb.create(ManInfo
        (
            "3 Turn Spin", "spin", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),            
            [ 
            MBTags.CENTRE,
            f3amb.spin(3),           
            f3amb.line(),
            f3amb.loop(np.pi/2),  
        ],
        ),
       
]#Close Sched_def array 
)    # close of Sched_def






if __name__ == "__main__":

    #intermediate_def.plot().show()
    #import os
    #intermediate_def.create_fcjs('f3auk_intermediate', f'{os.environ['HOME']}/Desktop/templates/')
    intermediate_def.to_json('flightanalysis/data/f3auk_inter_schedule.json')