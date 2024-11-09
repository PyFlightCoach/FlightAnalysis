import numpy as np

from flightanalysis.definition import ManParm, ManParms
from flightanalysis.builders.f3a.criteria import F3A
from flightanalysis.builders.f3a.downgrades import dg_applicator
from flightanalysis.builders.f3a.box import box

from ..elbuilders import line, loopmaker, rollmaker, spin, stallturn
from ..manbuilder import ManBuilder


imacmb = ManBuilder(
    ManParms(
        [
            ManParm("speed", F3A.inter.speed, 30.0, "m/s"),
            ManParm("loop_radius", F3A.inter.radius, 55.0, "m"),
            ManParm("line_length", F3A.inter.length, 130.0, "m"),
            ManParm("point_length", F3A.inter.length, 20.0, "m"),
            ManParm("partial_roll_rate", F3A.inter.roll_rate, np.pi, "rad/s"),
            ManParm("full_roll_rate", F3A.inter.roll_rate, np.pi, "rad/s"),
            ManParm("snap_rate", F3A.inter.roll_rate, 4 * np.pi, "rad/s"),
            ManParm("stallturn_rate", F3A.inter.roll_rate, 2 * np.pi, "rad/s"),
            ManParm("spin_rate", F3A.inter.roll_rate, 1.7 * np.pi, "rad/s"),
            ManParm("ee_pause", F3A.inter.length, 20.0, "m"),
        ]
    ),
    dict(
        line=dict(func=line, args=[], kwargs=dict(roll=0.0, speed=30.0, length=130)),
        loop=dict(
            func=loopmaker,
            args=["angle"],
            kwargs=dict(
                speed=30.0,
                radius=50,  #'loop_radius',
                rolls=0.0,
                ke=False,
                rollangle=None,
                rolltypes="roll",
                reversible=True,
                pause_length="point_length",
                break_angle=np.radians(15),
                snap_rate="snap_rate",
                break_rate=2 * np.pi,
                mode="imac",
            ),
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
                mode="imac",
                break_angle=np.radians(15),
                snap_rate="snap_rate",
                break_rate=2 * np.pi,
                rolltypes="roll",
            ),
        ),
        stallturn=dict(
            func=stallturn, args=[], kwargs=dict(speed=0.0, yaw_rate="stallturn_rate")
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
                mode="imac",
                break_angle=np.radians(15),
                snap_rate="snap_rate",
                break_rate=2 * np.pi,
                rolltypes="snap",
            ),
        ),
        spin=dict(
            func=spin,
            args=["turns"],
            kwargs=dict(
                speed=10,
                break_angle=np.radians(30),
                rate="spin_rate",
                break_rate=6,
                reversible=True,
            ),
        ),
    ),
    dg_applicator,
    F3A.inter,
    box
)
