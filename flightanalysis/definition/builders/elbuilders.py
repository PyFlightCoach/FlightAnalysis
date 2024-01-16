from ..eldef import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.elements import *
from flightdata import Collection
from flightanalysis.definition.collectors import Collectors
from flightanalysis.definition import Opp, ItemOpp
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.scoring import Combination
from numbers import Number
import numpy as np


def line(name, speed, length, roll):
    return ElDef.build(Line, name, speed, length, roll), ManParms()

def loop(name, speed, radius, angle, roll, ke):
    mps = ManParms()
    ed = ElDef.build(Loop, name, speed, radius, angle, roll, ke)
    
    return ed, mps

def roll(name, speed, rate, rolls):
    el = ElDef.build(Line, name, speed, abs(rolls) * speed / rate, rolls)
    if isinstance(rate, ManParm):
        rate.collectors.add(el.get_collector("rate"))
    return el, ManParms()

def stallturn(name, speed, yaw_rate):
    return ElDef.build(StallTurn, name, speed, yaw_rate), ManParms()

def snap(name, rolls, break_angle, rate, speed, break_rate):
    '''This will create a snap'''
    eds = ElDefs()
    mps = ManParms()

    #if isinstance(break_angle, Number):
    #    break_angle = ManParm(
    #        f"break_angle_{name}",
    #        Combination(desired=[[break_angle], [-break_angle]]),
    #        0
    #    )
    #    mps.add(break_angle)
    
    eds.add(ElDef.build(PitchBreak, f"{name}_break", speed=speed, 
        length=speed * abs(break_angle)/break_rate, break_angle=break_angle))
    
    eds.add(ElDef.build(Autorotation, f"{name}_autorotation", speed=speed,
        length=speed*abs(rolls)/rate, roll=rolls))
    
    eds.add(ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * abs(break_angle)/break_rate))
     
    return eds, mps


def spin(name, turns, break_angle, rate, speed, break_rate, reversible):   
    
    nose_drop = ElDef.build(NoseDrop, f"{name}_break", speed=speed, 
                      radius=speed * break_angle/break_rate, break_angle=break_angle)
    
    autorotation = ElDef.build(Autorotation, f"{name}_autorotation", speed=speed,
                        length=(speed * abs(turns))/rate, roll=turns)
    if isinstance(rate, ManParm):
        rate.collectors.add(autorotation.get_collector("rate"))

    recovery = ElDef.build(Recovery, f"{name}_recovery", speed=speed,
                    length=speed * break_angle/break_rate)
    return ElDefs([nose_drop, autorotation, recovery]), ManParms()


def roll_length(speed, angle, rate):
    return speed * roll_length(angle, rate)

def roll_duration(angle, rate):
    return abs(angle) / rate

def snap_length(speed, roll, break_angle, break_rate, snap_rate):
    return speed * snap_duration(roll, break_angle, break_rate, snap_rate)

def snap_duration(roll, break_angle, break_rate, snap_rate):
    return (2 * abs(break_angle) / break_rate + abs(roll) / snap_rate)


def short_line(name, speed, length, roll, extra_length):
    if length.__class__.__name__ == 'ManParm':
        el = ElDef.build(Line, name, speed, length.default, roll)
        length.append(el.get_collector('length') + extra_length), ManParms()
        return el
    else:
        return line(name, speed, length, roll)


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

        if rolltypes[i] == 'r':
            if r < 2*np.pi and mode=='f3a':
                if isinstance(partial_rate, ManParm):
                    partial_rate.collectors.add(eds[-1].get_collector("rate"))
            else:
                if isinstance(full_rate, ManParm):
                    full_rate.collectors.add(eds[-1].get_collector("rate"))
        else:
            snap_rate.collectors.add(eds[-2].get_collector("rate"))

        if i < rolls.n - 1 and (mode=='imac' or np.sign(r) == np.sign(rolls.value[i+1])):
            eds.add(short_line(
                f"{name}_{i+1}_pause",
                speed, pause_length, 0, 30
            ))
                            
    return eds, ManParms()


def pad(speed, line_length, eds: ElDefs):
    '''This will add pads to the ends of the element definitions to
      make the total length equal to line_length'''
    if isinstance(eds, ElDef):
        eds = ElDefs([eds])

    pad_length = 0.5 * (line_length - eds.builder_sum("length"))
    
    e1, mps = line(f"e_{eds[0].id}_pad1", speed, pad_length, 0)
    e3, mps = line(f"e_{eds[0].id}_pad2", speed, pad_length, 0)
    
    mp = ManParm(
        f"e_{eds[0].id}_pad_length", 
        F3A.inter.length,
        None, 
        Collectors([e1.get_collector("length") + 40, e3.get_collector("length") + 40])
    ) # TODO added 40 here as pads tend to be short. This needs to be more transparent.
    eds = ElDefs([e1] + [ed for ed in eds] + [e3])

    if isinstance(line_length, ManParm):
        line_length.append(eds.collector_sum("length", f"e_{eds[0].id}"))
    
    return eds, ManParms([mp])


def rollmaker(name, rolls, rolltypes, speed, partial_rate, 
    full_rate, pause_length, line_length, reversible, 
    break_angle, snap_rate, break_rate,
    padded, mode):
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
        eds, padmps = pad(speed, line_length, eds)
        mps.add(padmps)

    return eds, mps


def loopmaker(name, speed, radius, angle, rolls, ke, rollangle, rolltypes, reversible, pause_length,
    break_angle, snap_rate, break_rate, mode ):
    '''This will create a set of ElDefs to represent a series of loops and the pads at the ends if padded==True.'''

    ke = 0 if not ke else np.pi/2

    if rollangle is None:
        rollangle = angle

    if (isinstance(rolls, Number) or isinstance(rolls, ItemOpp) ) and rollangle == angle:
        return loop(name, speed, radius, angle, rolls, ke)
    
    mps = ManParms()
    eds = ElDefs()

    if isinstance(radius, Number):
        rad = radius
    else:
        rad = radius.value
    
    internal_rad = ManParm(f'{name}_radius', F3A.inter.free, rad )


    rolls = mps.parse_rolls(rolls, name, reversible) if not rolls==0 else 0

    try:
        rvs = rolls.value
    except Exception as e:
        rvs = None
    
    if rvs is None:
        multi_rolls = False 
        rvs = [rolls]
    else:
        multi_rolls = True


    rolltypes = parse_rolltypes(rolltypes, len(rvs))

    angle = ManParm.parse(angle, mps)



    if not rollangle == angle:
        eds.add(loop(f"{name}_pad1", speed, internal_rad, (angle - rollangle) / 2, 0, ke)[0])



    if multi_rolls:
        
        #TODO cannot cope with options that change whether a pause is required or not.
        #this will need to be covered in some other way
        if mode == 'f3a':
            has_pause = np.concatenate([np.diff(np.sign(rvs)), np.ones(1)]) == 0
        else:
            has_pause = np.concatenate([np.full(len(rvs)-1 , True), np.full(1, False)])

        pause_angle = pause_length / internal_rad
    
        #snapangle = 0
        #for i, rt in enumerate(rolltypes):
        #    if rt=='s':
        #        snapangle = snapangle + snap_length(speed, rvs[i], break_angle, break_rate, snap_rate) / internal_rad
        
        if np.sum(has_pause) == 0:
            remaining_rollangle = rollangle
        else:
            remaining_rollangle =  rollangle - pause_angle * np.sum(has_pause) #- snapangle

        only_rolls = []
        for i, rt in enumerate(rolltypes):
            only_rolls.append(abs(rvs[i]) if rt=='r' else 0)
        only_rolls = np.array(only_rolls)
        
        rolls.criteria.append_roll_sum(inplace=True)
        rvs = rolls.value

        loop_proportions = (np.abs(only_rolls) / np.sum(np.abs(only_rolls)))

        loop_angles = [remaining_rollangle * rp for rp in loop_proportions]

        n = len(loop_angles)

        for i, r in enumerate(loop_angles):    
            roll_done = rvs[i+n-1] if i > 0 else 0
            if rolltypes[i] == 'r':
                
                eds.add(loop(f"{name}_{i}", speed, internal_rad, r, rvs[i], ke=ke-roll_done)[0])
            else:
                ed, mps = snap(
                    f"{name}_{i}", rvs[i], break_angle, snap_rate, speed, break_rate
                )
                eds.add(ed)
                snap_rate.collectors.add(eds[-2].get_collector("rate"))
            
            if has_pause[i]:
                eds.add(loop(f"{name}_{i}_pause", speed, internal_rad, pause_angle, 0, ke=ke-rvs[i+n])[0])


        ke=ke-rvs[i+n]
        
    else:
        eds.add(loop(f"{name}_rolls", speed, internal_rad, rollangle, rolls, ke=ke)[0])
        ke = ke - rolls




    if not rollangle == angle:
        eds.add(loop(f"{name}_pad2", speed, internal_rad, (angle - rollangle) / 2, 0, ke)[0])
    mps.add(internal_rad)
    return eds, mps