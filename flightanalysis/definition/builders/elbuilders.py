from ..eldef import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.elements import Line, Loop, StallTurn, PitchBreak, Autorotation, Recovery, NoseDrop
from flightanalysis.definition.collectors import Collectors
from flightanalysis.definition import ItemOpp
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.scoring.f3a_downgrades import DGGrps
from flightanalysis.scoring.downgrade import DownGrades
from numbers import Number
import numpy as np


def line(name: str, speed, length, soft_start=False, soft_end=False):
    dgs = DGGrps.line
    if soft_start:
        dgs = DGGrps.line_accel
    if soft_end:
        dgs = DGGrps.line_decel
    return ElDef.build(
        Line, name, 
        [speed, length],
        dgs, 
    ), ManParms()

def roll(name: str, speed, rate, rolls):
    el = ElDef.build(
        Line, name, 
        [speed, abs(rolls) * speed / rate, rolls],
        DGGrps.roll,
    )
    if isinstance(rate, ManParm):
        rate.collectors.add(el.get_collector("rate"))
    return el, ManParms()

def loop(name: str, speed, radius, angle, ke):
    ed = ElDef.build(
        Loop, name, 
        [speed, angle, radius, 0, ke],
        DGGrps.loop,
    )
    return ed, ManParms()

def rolling_loop(name, speed, radius, angle, roll, ke):
    ed = ElDef.build(
        Loop, name, 
        [speed, angle, radius, roll, ke],
        DGGrps.rolling_loop,
    )
    return ed, ManParms()

def stallturn(name, speed, yaw_rate):
    return ElDef.build(
        StallTurn, name, 
        [speed, yaw_rate],
        DGGrps.stallturn, 
    ), ManParms()

def snap(name, rolls, break_angle, rate, speed, break_rate):
    '''This will create a snap'''
    eds = ElDefs()
    
    eds.add(ElDef.build(
        PitchBreak, f"{name}_break", 
        [speed, speed * abs(break_angle)/break_rate, break_angle],
        DGGrps.pitch_break,
    ))
    
    eds.add(ElDef.build(
        Autorotation, f"{name}_autorotation", 
        [speed, speed*abs(rolls)/rate, rolls],
        DGGrps.autorotation
    ))

    if isinstance(rate, ManParm):
        rate.collectors.add(eds[-1].get_collector("rate"))
    
    eds.add(ElDef.build(
        Recovery, f"{name}_recovery", 
        [speed, speed * abs(break_angle)/break_rate],
        DGGrps.recovery,
    ))
     
    return eds, ManParms()


def spin(name, turns, break_angle, rate, speed, break_rate, reversible):   
    
    nose_drop = ElDef.build(
        NoseDrop, f"{name}_break", 
        [speed, speed * break_angle/break_rate, break_angle],
        DGGrps.nose_drop, 
    )

    #if isinstance(turns, Number):
    #    turns = ManParm(f"{name}_rolls", 
    #        Combination.rolllist(
    #            [turns] if np.isscalar(turns) else turns, 
    #            reversible
    #    ), 0) 

    autorotation = ElDef.build(
        Autorotation, f"{name}_autorotation", 
        [speed, speed * abs(turns)/rate, turns],
        DGGrps.autorotation
    )

    if isinstance(rate, ManParm):
        rate.collectors.add(autorotation.get_collector("rate"))

    recovery = ElDef.build(
        Recovery, f"{name}_recovery", 
        [speed, speed * break_angle/break_rate],
        DGGrps.recovery,
    )

    return ElDefs([nose_drop, autorotation, recovery]), ManParms()


def parse_rolltypes(rolltypes, n):
    
    if rolltypes == 'roll' or rolltypes is None:
        return ''.join(['r' for _ in range(n)])
    elif rolltypes == 'snap':
        return ''.join(['s' for _ in range(n)])
    else:
        assert len(rolltypes) == len(range(n))
        return rolltypes


def roll_combo(
        name, speed, rolls, rolltypes, 
        partial_rate, full_rate, pause_length,
        break_angle, snap_rate, break_rate, mode) -> ElDefs:
    '''This creates a set of ElDefs to represent a list of rolls or snaps
      and pauses between them if mode==f3a it does not create pauses when roll direction is reversed
    '''
    eds = ElDefs()
    rolltypes = parse_rolltypes(rolltypes, len(rolls.value))

    for i, r in enumerate(rolls.value):
        if rolltypes[i] == 'r':
            eds.add(roll(
                f"{name}_{i}", speed,
                partial_rate if abs(r) < 2*np.pi else full_rate,
                rolls[i]
            )[0])
        else:
            eds.add(snap(
                f"{name}_{i}", rolls[i], break_angle, snap_rate, speed, break_rate
            )[0])

        if i < rolls.n - 1 and (mode=='imac' or np.sign(r) == np.sign(rolls.value[i+1])):
            eds.add(line(f"{name}_{i+1}_pause", speed, pause_length))
                            
    return eds, ManParms()


def pad(speed, line_length, eds: ElDefs, soft_start: bool = False, soft_end: bool = False):
    '''This will add pads to the ends of the element definitions to
      make the total length equal to line_length'''
    eds = ElDefs([eds]) if isinstance(eds, ElDef) else eds
    
    pad_length = 0.5 * (line_length - eds.builder_sum("length"))
    
    e1 = line(f"e_{eds[0].id}_pad1", speed, pad_length, soft_start, False)[0]
    e3 = line(f"e_{eds[0].id}_pad2", speed, pad_length, False, soft_end)[0]
    
    mp = ManParm(
        f"e_{eds[0].id}_pad_length", 
        F3A.inter.length,
        collectors = Collectors([e1.get_collector("length"), e3.get_collector("length")])
    )

    eds = ElDefs([e1] + [ed for ed in eds] + [e3])

    if isinstance(line_length, ManParm):
        line_length.append(eds.collector_sum("length", f"e_{eds[0].id}"))
    
    return eds, ManParms([mp])


def rollmaker(name, rolls, rolltypes, speed, partial_rate, 
    full_rate, pause_length, line_length, reversible, 
    break_angle, snap_rate, break_rate,
    padded, mode, soft_start, soft_end):
    '''This will create a set of ElDefs to represent a series of rolls or snaps
      and pauses between them and the pads at the ends if padded==True.
    '''
    mps = ManParms()

    _rolls = mps.parse_rolls(rolls, name, reversible)         
    
    if isinstance(_rolls, ItemOpp):
        
        if rolltypes[0] == 'r':
            _r=_rolls.a.value[_rolls.item]
            rate = full_rate if abs(_r)>=2*np.pi else partial_rate
            eds, rcmps = roll(f"{name}_roll", speed, rate, _rolls)
        else:
            eds, rcmps = snap(f"{name}_snap", _rolls, break_angle, snap_rate, speed, break_rate)
    else:
        eds, rcmps = roll_combo(
            name, speed, _rolls, rolltypes, 
            partial_rate, full_rate, pause_length,
            break_angle, snap_rate, break_rate, mode
        )
        
    mps.add(rcmps)
            
    if padded:
        eds, padmps = pad(speed, line_length, eds, soft_start, soft_end)
        mps.add(padmps)

    return eds, mps


def loopmaker(name, speed, radius, angle, rolls, ke, rollangle, rolltypes, reversible, pause_length,
    break_angle, snap_rate, break_rate, mode ):
    '''This will create a set of ElDefs to represent a series of loops and the pads at the ends if padded==True.'''

    
    ke = 0 if not ke else np.pi/2
    rollangle = angle if rollangle is None else rollangle
    
    if rolls == 0:
        return loop(name, speed, radius, angle, ke)
    if (isinstance(rolls, Number) or isinstance(rolls, ItemOpp) ) and rollangle == angle:
        return rolling_loop(name, speed, radius, angle, rolls, ke)
    
    mps = ManParms()
    eds = ElDefs()

    rad = radius if isinstance(radius, Number) else radius.value

    internal_rad = ManParm(f'{name}_radius', F3A.inter.free, rad )

    rolls = mps.parse_rolls(rolls, name, reversible) if not rolls==0 else 0

    try:
        rvs = rolls.value
    except Exception:
        rvs = None
    
    multi_rolls = rvs is not None
    rvs = [rolls] if rvs is None else rvs  

    rolltypes = parse_rolltypes(rolltypes, len(rvs))

    angle = ManParm.parse(angle, mps)

    if not rollangle == angle:
        eds.add(loop(f"{name}_pad1", speed, internal_rad, (angle - rollangle) / 2, ke)[0])

    if multi_rolls:
        #TODO cannot cope with options that change whether a pause is required or not.
        #this will need to be covered in some other way
        if mode == 'f3a':
            has_pause = np.concatenate([np.diff(np.sign(rvs)), np.ones(1)]) == 0
        else:
            has_pause = np.concatenate([np.full(len(rvs)-1 , True), np.full(1, False)])

        pause_angle = pause_length / internal_rad
    
        if np.sum(has_pause) == 0:
            remaining_rollangle = rollangle
        else:
            remaining_rollangle =  rollangle - pause_angle * np.sum(has_pause)

        only_rolls = []
        for i, rt in enumerate(rolltypes):
            only_rolls.append(abs(rvs[i]) if rt=='r' else 0)
        only_rolls = np.array(only_rolls)
        
        rolls.criteria.append_roll_sum(inplace=True)

        loop_proportions = (np.abs(only_rolls) / np.sum(np.abs(only_rolls)))

        loop_angles = [remaining_rollangle * rp for rp in loop_proportions]

        n = len(loop_angles)

        for i, r in enumerate(loop_angles):    
            roll_done = rolls[i+n-1] if i > 0 else 0
            if rolltypes[i] == 'r':
                
                eds.add(rolling_loop(f"{name}_{i}", speed, internal_rad, r, rolls[i], ke=ke - roll_done)[0]) 
            else:
                ed, mps = snap(
                    f"{name}_{i}", rolls[i], break_angle, snap_rate, speed, break_rate
                )
                eds.add(ed)
                snap_rate.collectors.add(eds[-2].get_collector("rate"))
            
            if has_pause[i]:
                eds.add(loop(f"{name}_{i}_pause", speed, internal_rad, pause_angle, ke=ke - rolls[i+n])[0]) 

        ke=ke-rolls[i+n]
        
    else:
        eds.add(rolling_loop(f"{name}_rolls", speed, internal_rad, rollangle, rolls, ke=ke)[0])
        ke = ke - rolls

    if not rollangle == angle:
        eds.add(loop(f"{name}_pad2", speed, internal_rad, (angle - rollangle) / 2, ke)[0])
    mps.add(internal_rad)
    return eds, mps