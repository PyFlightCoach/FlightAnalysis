'''
UKF3A Clubman template
Author Vince Beesley
'''
from flightanalysis import *
import numpy as np

clubman_def = SchedDef([  

    f3amb.create(ManInfo
        (
            "Turn Round", "trnround", k=0, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[  
            f3amb.loop(np.pi/4),
            centred(f3amb.roll(np.pi, line_length = 2*65)),
            f3amb.loop(5*np.pi/4),     
        ],
        loop_radius=65),    
    
    f3amb.create(ManInfo("Inside Loop", "inloop", k=2, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),
        [               
            MBTags.CENTRE,
            f3amb.loop(2*np.pi, radius=100),
            MBTags.CENTRE,                          
        ],
        ),

    f3amb.create(ManInfo
        (
            "Half Rev Cuban 8", "rcuban", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[  
            f3amb.loop(np.pi/4),
            centred(f3amb.roll(np.pi, line_length = 2*65)),
            f3amb.loop(5*np.pi/4),     
        ],
        loop_radius=65),

     f3amb.create(ManInfo(
            "slow Roll", "slowroll", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
           f3amb.roll(2*np.pi, full_rate = np.pi/2, padded=False),
        ],),       

     f3amb.create(ManInfo
        (
            "Half Cuban 8", "hcuban", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[  
            f3amb.loop(np.pi/4),
            centred(f3amb.roll(np.pi, line_length = 2*45)),
            f3amb.loop(5*np.pi/4),     
        ],
        loop_radius=45),
        
    f3amb.create(ManInfo(
            "Immelman combo", "Immel", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)            
        ),
        [             
            f3amb.loop(np.pi),
            f3amb.roll(np.pi , padded=False),            
            f3amb.line(length=30), 
            f3amb.roll(np.pi , padded=False),          
            f3amb.loop(np.pi),                     
           ], 
            loop_radius = 100 ),
    f3amb.create(ManInfo(
            "Humpty", "innerhB", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),
        [            
            f3amb.loop(np.pi/2),
            f3amb.roll(np.pi),                     
            f3amb.loop(np.pi),
            f3amb.line(),            
            f3amb.loop(np.pi/2),           
        ]),


   f3amb.create(ManInfo(
            "Inverted Flight", "inverted", k=2, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
           f3amb.roll(np.pi, padded=False),           
           f3amb.line(length = 100),          
           f3amb.roll(np.pi, padded=False),          
          ]),

    f3amb.create(ManInfo(
            "Stall Turn", "stall", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),
        [
            f3amb.loop(np.pi/2),
            f3amb.line(length=150),                       
            f3amb.line(speed = 3, length = 10),
            f3amb.line(speed = 1, length = 5),
            f3amb.stallturn(),
            f3amb.line(length=165), 
            f3amb.loop(np.pi/2)
        ]),

    f3amb.create(ManInfo(
            "Outside Loop", "outloop", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),
        [        
            f3amb.roll(np.pi, padded=False),
            f3amb.line(length='ee_pause'),
            MBTags.CENTRE,
            f3amb.loop(-2*np.pi, radius=100),
            MBTags.CENTRE,
            f3amb.line(length='ee_pause'),  
            f3amb.roll(np.pi, padded=False),            
        ],
        ),
    f3amb.create(ManInfo(
            "Outer Humpty", "outerhB", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            
            f3amb.loop(np.pi/2), 
            f3amb.line(),                              
            f3amb.loop(np.pi),
            f3amb.roll(np.pi),            
            f3amb.loop(np.pi/2)]),

    f3amb.create(ManInfo
        (
            "Cuban 8", "fullcuban8", k=2, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[  
            f3amb.loop(5*np.pi/4),            
            centred(f3amb.roll(np.pi)),                       
            f3amb.loop(3*np.pi/2), 
            centred(f3amb.roll(np.pi)),                    
            f3amb.loop(np.pi/4),          
        ],
        loop_radius = 100, line_length = 200,
        ),

     f3amb.create(ManInfo
        (
            "Half Sqr Loop", "hsqrloop", k=2, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),            
            [  
            f3amb.loop(np.pi/2),           
            centred(f3amb.roll(np.pi)),
            f3amb.loop(-np.pi/2),  
        ],
        ),

    f3amb.create(ManInfo
        (
            "3 Turn Spin", "spin", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),            
            [ 
            MBTags.CENTRE,
            f3amb.spin(r(3)),
            f3amb.line(),
            f3amb.loop(np.pi/2),  
        ],
        ),
    
    f3amb.create(ManInfo
        (
            "Landing", "land", k=1, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),            
            [ 
             f3amb.line(),
             ],
        ),
    ]
)



if __name__ == "__main__":

#    clubman_def.plot().show()
    clubman_def.to_json("flightanalysis/data/f3auk_clubman_schedule.json")

#    import os
#    clubman_def.create_fcjs('f3auk_clubman', f'{os.environ['HOME']}/Desktop/templates/')