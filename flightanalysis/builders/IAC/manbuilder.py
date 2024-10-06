import numpy as np

from flightanalysis.definition import ManParm, ManParms
from flightanalysis.builders.IAC.criteria import IAC
from flightanalysis.builders.IAC.downgrades import dg_applicator
from flightanalysis.builders.IAC.box import unlimited_box
from ..elbuilders import line, loopmaker, rollmaker, spin, stallturn
from ..manbuilder import ManBuilder


_snap_rate = 3*np.pi
_roll_rate = np.pi
_spin_rate = np.pi / 2
_speed = 60
_break_angle = np.radians(20)

iacmb = ManBuilder(
    ManParms(
        [
            ManParm("speed", IAC.inter.speed, _speed, "m/s"),
            ManParm("loop_radius", IAC.inter.radius, 70.0, "m"),
            ManParm("line_length", IAC.inter.length, 180.0, "m"),
            ManParm("point_length", IAC.inter.length, 20.0, "m"),
            ManParm("partial_roll_rate", IAC.inter.roll_rate, _roll_rate, "rad/s"),
            ManParm("full_roll_rate", IAC.inter.roll_rate, _roll_rate, "rad/s"),
            ManParm("snap_rate", IAC.inter.roll_rate, _snap_rate, "rad/s"),
            ManParm("stallturn_rate", IAC.inter.roll_rate, np.pi/4, "rad/s"),
            ManParm("spin_rate", IAC.inter.roll_rate, _spin_rate, "rad/s"),
            ManParm("ee_pause", IAC.inter.length, 20.0, "m"),
        ]
    ),
    dict(
        line=dict(
            func=line,
            args=[],
            kwargs=dict(
                speed=_speed,
                length=180,
            ),
        ),
        loop=dict(
            func=loopmaker,
            args=["angle"],
            kwargs=dict(
                speed=40,
                radius=70,
                rolls=0.0,
                ke=False,
                rollangle=None,
                rolltypes="roll",
                reversible=True,
                pause_length="point_length",
                break_angle=_break_angle,
                snap_rate=_snap_rate,
                break_roll=np.pi / 4,
                recovery_roll=np.pi / 2,
                mode="imac",
            ),
        ),
        roll=dict(
            func=rollmaker,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed=40,
                line_length=180,
                partial_rate=_roll_rate,
                full_rate=_roll_rate,
                pause_length="point_length",
                mode="imac",
                break_angle=_break_angle,
                snap_rate=_snap_rate,
                break_roll=np.pi / 4,
                recovery_roll=np.pi / 2,
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
                speed=40,
                line_length=180,
                partial_rate=_roll_rate,
                full_rate=_roll_rate,
                pause_length="point_length",
                mode="imac",
                break_angle=np.radians(20),
                snap_rate=_snap_rate,
                break_roll=np.pi / 4,
                recovery_roll=np.pi / 2,
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
                nd_turns=np.pi / 4,
                recovery_turns=np.pi / 2,
            ),
        ),
    ),
    dg_applicator,
    IAC.inter,
    unlimited_box
)
