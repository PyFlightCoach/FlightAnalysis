from flightanalysis.definition import ManDef, ManParm, ManParms, ElDef, ElDefs, DummyMPs, Opp
from typing import Dict, Callable
from functools import partial
from .elbuilders import line, loopmaker, rollmaker, stallturn, spin
import numpy as np

class MBTags:
    CENTRE=0

def centred(elb):
    setattr(elb, 'centred', True)
    return elb


c45 = np.cos(np.radians(45))

def r(turns):
    return 2 * np.pi * np.array(turns)

dp = DummyMPs()



class ManBuilder():
    def __init__(self, mps: ManParms, mpmaps:Dict[str, dict]):
        self.mps = mps
        self.mpmaps = mpmaps

    def __getattr__(self, name):
        if name in self.mpmaps:
            return partial(self.el, name)
    
    def el(self, kind, *args, **kwargs):
        """Setup kwargs to pull defaults from mpmaps
        returns a function that appends the created elements to a ManDef"""
        
        all_kwargs = self.mpmaps[kind]["kwargs"].copy() # take the defaults
        for k,a in kwargs.items():
            all_kwargs[k]=a  # take the **kwargs if they were specified
        for k, a in zip(self.mpmaps[kind]["args"], args):
            if k in kwargs:
                raise ValueError(f"Argument {k} specified twice")
            all_kwargs[k] = a  # take the *args
        
        def append_el(md: ManDef, **kwargs) -> ElDefs:
            full_kwargs = {}
            for k, a in kwargs.items():
                if isinstance(a, Opp):
                    a = str(a) # serialise and parse again to make sure its coming from this mandef
                if isinstance(a, str):
                    try:
                        a = ManParm.parse(a, md.mps)
                    except Exception:
                        pass
                full_kwargs[k] = a
            
            eds, mps = self.mpmaps[kind]["func"](md.eds.get_new_name(),**full_kwargs)            
            neds = md.eds.add(eds)
            md.mps.add(mps)
            return neds
                        
        return partial(append_el, **all_kwargs)


    def create(self, maninfo, elmakers: list[Callable[[ManDef], ElDef]], **kwargs) -> ManDef:
        mps = self.mps.copy()
        for k, v in kwargs.items():
            if isinstance(v, ManParm):
                mps.add(v)
            elif isinstance(k, str):
                if k in mps.data:
                    mps[k].default=v
                else:
                    mps.add(ManParm.parse(v, mps, k))
        md = ManDef(maninfo, mps)
        for i, em in enumerate(elmakers):
            if isinstance(em, int):
                if em == MBTags.CENTRE:
                    md.info.centre_points.append(len(md.eds.data))
            else:
                c1 = len(md.eds.data)
                try:
                    new_eds = em(md)    
                except Exception as ex:
                    raise Exception(f"Error running elmaker {i} of {md.info.name}") from ex


                c2 = len(md.eds.data)

                if hasattr(em, 'centred'):
                    if c2 - c1 == 1:
                        
                        md.info.centred_els.append((c1, 0.5))
                            
                    else:
                        ceid, fac = ElDefs(new_eds).get_centre(mps) 
                        if abs(int(fac) - fac) < 0.05:
                            md.info.centre_points.append(c1 + ceid + int(fac))
                        else:
                            md.info.centred_els.append((ceid + c1, fac))  

        md.mps = md.mps.remove_unused()
        return md
        
from flightanalysis.scoring.criteria.f3a_criteria import F3A

f3amb = ManBuilder(
    ManParms([
        ManParm("speed", F3A.inter.speed, 30.0),
        ManParm("loop_radius", F3A.inter.radius, 55.0),
        ManParm("line_length", F3A.inter.length, 130.0),
        ManParm("point_length", F3A.inter.length, 20.0),
        ManParm("partial_roll_rate", F3A.inter.roll_rate, np.pi/2),
        ManParm("full_roll_rate", F3A.inter.roll_rate, 3*np.pi/4),
        ManParm("snap_rate", F3A.inter.roll_rate, 4*np.pi),
        ManParm("stallturn_rate", F3A.inter.roll_rate, np.pi),
        ManParm("spin_rate", F3A.inter.roll_rate, 1.7*np.pi),
        ManParm("ee_pause", F3A.inter.length, 20.0)
    ]),
    mpmaps=dict(
        line=dict(
            func=line,
            args=[],
            kwargs=dict(
                roll=0.0,
                speed=30.0,
                length="line_length"
            )
        ),
        loop=dict(
            func=loopmaker,
            args=["angle"],
            kwargs=dict(
                speed=30.0, 
                radius='loop_radius', 
                rolls=0.0, 
                ke=False, 
                rollangle=None, 
                rolltypes='roll', 
                reversible=True,
                pause_length="point_length",
                break_angle=np.radians(10), 
                snap_rate='snap_rate', 
                break_rate=2*np.pi, 
                mode='f3a'
            )
        ),
        roll=dict(
            func=rollmaker,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed=30.0,
                line_length="line_length",
                partial_rate="partial_roll_rate",
                full_rate="full_roll_rate",
                pause_length="point_length",
                mode='f3a',
                break_angle=np.radians(10), 
                snap_rate='snap_rate', 
                break_rate=2*np.pi,
                rolltypes='roll'
            )    
        ),
        stallturn=dict(
            func=stallturn,
            args=[],
            kwargs=dict(
                speed=0.0,
                yaw_rate="stallturn_rate"   
            )
        ),
        snap=dict(
            func=rollmaker,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed=30.0,
                line_length="line_length",
                partial_rate="partial_roll_rate",
                full_rate="full_roll_rate",
                pause_length="point_length",
                mode='f3a',
                break_angle=np.radians(10), 
                snap_rate='snap_rate', 
                break_rate=2*np.pi,
                rolltypes='snap'
            )    
        ),
        spin=dict(
            func=spin,
            args=["turns"],
            kwargs=dict(
                speed=10,
                break_angle=np.radians(30),
                rate="spin_rate",
                break_rate=6,
                reversible=True
            )
        )

    )
)


imacmb = ManBuilder(
    ManParms([
        ManParm("speed", F3A.inter.speed, 30.0),
        ManParm("loop_radius", F3A.inter.radius, 55.0),
        ManParm("line_length", F3A.inter.length, 130.0),
        ManParm("point_length", F3A.inter.length, 20.0),
        ManParm("partial_roll_rate", F3A.inter.roll_rate, np.pi),
        ManParm("full_roll_rate", F3A.inter.roll_rate, np.pi),
        ManParm("snap_rate", F3A.inter.roll_rate, 4*np.pi),
        ManParm("stallturn_rate", F3A.inter.roll_rate, 2*np.pi),
        ManParm("spin_rate", F3A.inter.roll_rate, 1.7*np.pi),
        ManParm("ee_pause", F3A.inter.length, 20.0)
    ]),
    mpmaps=dict(
        line=dict(
            func=line,
            args=[],
            kwargs=dict(
                roll=0.0,
                speed=30.0,
                length=130
            )
        ),
        loop=dict(
            func=loopmaker,
            args=["angle"],
            kwargs=dict(
                speed=30.0, 
                radius=50,#'loop_radius', 
                rolls=0.0, 
                ke=False, 
                rollangle=None, 
                rolltypes='roll', 
                reversible=True,
                pause_length="point_length",
                break_angle=np.radians(15), 
                snap_rate='snap_rate', 
                break_rate=2*np.pi, 
                mode='imac'
            )
        ),
        roll=dict(
            func=rollmaker,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed=30.0,
                line_length=130,
                partial_rate="partial_roll_rate",
                full_rate="full_roll_rate",
                pause_length="point_length",
                mode='imac',
                break_angle=np.radians(15), 
                snap_rate='snap_rate', 
                break_rate=2*np.pi,
                rolltypes='roll'
            )    
        ),
        stallturn=dict(
            func=stallturn,
            args=[],
            kwargs=dict(
                speed=0.0,
                yaw_rate="stallturn_rate"   
            )
        ),
        snap=dict(
            func=rollmaker,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed=30.0,
                line_length="line_length",
                partial_rate="partial_roll_rate",
                full_rate="full_roll_rate",
                pause_length="point_length",
                mode='imac',
                break_angle=np.radians(15), 
                snap_rate='snap_rate', 
                break_rate=2*np.pi,
                rolltypes='snap'
            )    
        ),
        spin=dict(
            func=spin,
            args=["turns"],
            kwargs=dict(
                speed=10,
                break_angle=np.radians(30),
                rate="spin_rate",
                break_rate=6,
                reversible=True
            )
        )

    )
)
