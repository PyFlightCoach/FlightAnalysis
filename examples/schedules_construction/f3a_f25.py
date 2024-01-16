from flightanalysis.definition import *
from flightanalysis.elements import *
from flightanalysis.scoring.criteria import *
import numpy as np

c45 = np.cos(np.radians(45))



f25_def = SchedDef([
    f3amb.create(ManInfo(
            "Square on Corner", "sLoop", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi/4, rolls="roll_option[0]"),
            f3amb.line(),
            f3amb.loop("roll_option[1]", rolls=r(1/2), ke=True),
            f3amb.line(),
            centred(f3amb.loop("roll_option[2]", rolls=r(1/2), ke=True)),
            f3amb.line(),
            f3amb.loop("roll_option[3]", rolls=r(1/2), ke=True),
            f3amb.line(),
            f3amb.loop("roll_option[4]", rolls="roll_option[5]", ke=True),
            MBTags.CENTRE
        ], 
        roll_option=ManParm("roll_option", Combination(desired=[
            [r(1/4), -r(1/4), r(1/4), -r(1/4), r(1/8), -r(1/4)], 
            [-r(1/4), r(1/4), -r(1/4), r(1/4), -r(1/8), r(1/4)]
        ]), 0),
        line_length=70
        ),
    f3amb.create(ManInfo(
            "Figure P", "fig9", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll([2*np.pi,-np.pi]),
            f3amb.loop(-3*np.pi/2),
        ], full_roll_rate=np.pi, partial_roll_rate=np.pi ),
    f3amb.create(ManInfo(
            "Roll Combo", "rollC", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            centred(f3amb.roll(
                [np.pi/2, np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2, np.pi/2, np.pi/2], 
                padded=False
            ))
        ], ),
    f3amb.create(ManInfo(
            "Half Loop", "hLoop", k=4, position=Position.END, 
            start=BoxLocation(Height.MID, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi, rolls=np.pi)
        ], ),
    f3amb.create(ManInfo(
            "Humpty", "hB", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.snap(r(1.5)),
            centred(f3amb.loop(np.pi, rolls=np.pi)),
            f3amb.roll(r(1.5)),
            f3amb.loop(-np.pi/2)
        ], full_roll_rate=np.pi),
    f3amb.create(ManInfo(
            "Spins", "spin", k=3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.spin(r(3)),
            f3amb.roll(r(0.5), line_length=147),
            f3amb.loop(np.pi/2)
        ], ),
    f3amb.create(ManInfo(
            "Rolling Circle", "hCirc", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            MBTags.CENTRE,
            f3amb.loop("roll_option[0]", rolls="roll_option[1]", ke=True),
            centred(f3amb.loop("roll_option[2]", rolls="roll_option[3]", ke=True)),
            f3amb.loop("roll_option[4]", rolls="roll_option[5]", ke=True),
            MBTags.CENTRE
        ], 
        loop_radius=100,
         roll_option=ManParm("roll_option", Combination(desired=[
            [np.pi/2, np.pi, -np.pi, -np.pi, np.pi/2, np.pi], 
            [-np.pi/2, -np.pi, np.pi, np.pi, -np.pi/2, -np.pi]
        ]), 1),
        ),
    f3amb.create(ManInfo(
            "Shark Fin", "sFin", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll('2/2'),
            f3amb.loop(-3*np.pi/4),
            f3amb.snap([r(1), r(-1)], line_length=str(f3amb.mps.line_length / c45 + 2*f3amb.mps.loop_radius)),
            #L2 = (L1 + 2*R - 2*R(1-c45)) / c45
            #L2 = (L1/c45 + 2*R)
            f3amb.loop(np.pi/4)
        ], line_length=80, full_roll_rate=np.pi, loop_radius=40),
    f3amb.create(ManInfo(
            "Square Octagonal Loop", "sV8", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll(r(0.5)),
            f3amb.loop(-np.pi/2),
            centred(f3amb.roll(2*np.pi)),
            f3amb.loop(np.pi/2),
            f3amb.roll("roll_option[0]"),
            f3amb.loop("roll_option[1]", ke=True),
            centred(f3amb.roll(2*np.pi)),
            f3amb.loop("roll_option[2]", ke=True),
            f3amb.roll("roll_option[3]"),
            f3amb.loop(-np.pi/2),
            centred(f3amb.roll(2*np.pi)),
            f3amb.loop(np.pi/2),
            f3amb.roll('1/2'),
            f3amb.loop(-np.pi/2)
        ], line_length=60, full_roll_rate=3*np.pi/2, partial_roll_rate=3*np.pi/2, loop_radius=35,
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi/2, -np.pi/2, np.pi/2], 
                [-np.pi/2, np.pi/2, np.pi/2, -np.pi/2]
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "Humpty_2", "hB2", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED), 
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll('1/2'),
            f3amb.loop(-np.pi),
            f3amb.roll('3/2'),
            f3amb.loop(np.pi/2),
        ], ),
    f3amb.create(ManInfo(
            "Triangular Loop", "keTrg", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(r(3/8), rolls="roll_option[0]"),
            f3amb.roll(r(1/2)),
            centred(f3amb.loop("roll_option[1]", rolls="top_roll_option[0]", ke=True)),
            f3amb.roll(r(1/2)),
            f3amb.loop("roll_option[2]", rolls="roll_option[3]", ke=True)
        ], 
        roll_option=ManParm("roll_option", Combination(desired=r([
                [-1/4, -1/4, -3/8, -1/4], 
                [1/4, 1/4, 3/8, 1/4]
            ])), 0),
        top_roll_option=ManParm("top_roll_option", Combination(desired=r([[-1/2], [1/2]])), 0),
    ),
    f3amb.create(ManInfo(
            "Half 8 Sided Loop", "h8L", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("roll_option[0]"),
            f3amb.loop("roll_option[1]", ke=True),
            f3amb.line(),
            f3amb.loop("roll_option[2]", ke=True),
            f3amb.roll("roll_option[3]"),
            f3amb.loop(np.pi/4)
        ], line_length=65, loop_radius=35,
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi/4, -np.pi/4, -np.pi/2], 
                [-np.pi/2, np.pi/4, np.pi/4, np.pi/2]
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "45 degree downline", "dl45", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/4),
            centred(f3amb.roll([r(1.25), -r(1.25)])),
            f3amb.loop(-np.pi/4)
        ], full_roll_rate=np.pi, line_length=231/c45 - (2/c45-2)*55 ),
        #231/c45 - (2/c45-2)*R)= L
    f3amb.create(ManInfo(
            "Half Square Loop", "hSLoop", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi/2),
            f3amb.roll([2*np.pi, - np.pi]),
            f3amb.loop(np.pi/2)
        ], full_roll_rate=np.pi, partial_roll_rate=np.pi ),
    f3amb.create(ManInfo(
            "Avalanche", "Aval", k=6, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi/2, rolls="roll_option[0]"),
            f3amb.loop("roll_option[1]", ke=True),
            centred(f3amb.snap(r(1), padded=False)),
            f3amb.loop("roll_option[2]", ke=True),
            f3amb.loop("roll_option[3]", rolls="roll_option[4]", ke=True),
            MBTags.CENTRE
        ], loop_radius=100, 
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2], 
                [-np.pi/2, np.pi/2, np.pi/2, np.pi/2, np.pi/2]
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "Split S", "keS", k=4, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll("roll_option[0]", padded=False),
            f3amb.loop("roll_option[1]", ke=True),
            f3amb.roll("roll_option[2]", padded=False)
        ], loop_radius=122.5,
        roll_option=ManParm("roll_option", Combination(desired=[
                [np.pi/2, -np.pi, np.pi/2], 
                [-np.pi/2, np.pi, -np.pi/2],
            ]), 0),
        ),
    f3amb.create(ManInfo(
            "Stall Turn", "stall", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll('1/2', padded=False),
            f3amb.line(length="ee_pause"),
            f3amb.loop(np.pi/2),
            MBTags.CENTRE,
            f3amb.roll("3x4"),
            f3amb.stallturn(),
            f3amb.snap(r(0.75)),
            f3amb.loop(-np.pi/2),
            f3amb.line(length="ee_pause"),
            f3amb.roll('1/2', padded=False),
        ], 
        line_length=150,
        partial_roll_rate=np.pi,
        ee_pause=10,
        #roll_option=need to thing about how to do this
    )
])



if __name__ == "__main__":

 
    #f25_def.plot().show()
#    f25_def.create_fcj('F25', 'f25_template_fcj.json')
    f25_def.to_json("flightanalysis/data/f3a_f25_schedule.json")
    #import os
    #f25_def.create_fcjs('f25', f'{os.environ['HOME']}/Desktop/templates/')