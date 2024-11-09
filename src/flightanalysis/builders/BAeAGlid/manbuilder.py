import numpy as np

from flightanalysis.definition import ManParm, ManParms
from flightanalysis.builders.BAeAGlid.criteria import Glider
from flightanalysis.builders.IAC.downgrades import dg_applicator
from flightanalysis.builders.BAeAGlid.box import box
from ..elbuilders import line, loopmaker, rollmaker, spin, stallturn
from ..manbuilder import ManBuilder


glidmb = ManBuilder(
    ManParms(
        [
            ManParm("speed", Glider.inter.speed, 45.0, "m/s"),
            ManParm("loop_radius", Glider.inter.radius, 40.0, "m"),
            ManParm("line_length", Glider.inter.length, 200.0, "m"),
            ManParm("point_length", Glider.inter.length, 20.0, "m"),
            ManParm("partial_roll_rate", Glider.inter.roll_rate, np.pi / 2, "rad/s"),
            ManParm("full_roll_rate", Glider.inter.roll_rate, np.pi / 2, "rad/s"),
            ManParm("snap_rate", Glider.inter.roll_rate, np.pi, "rad/s"),
            ManParm("stallturn_rate", Glider.inter.roll_rate, np.pi/4, "rad/s"),
            ManParm("spin_rate", Glider.inter.roll_rate, 1.7 * np.pi/4, "rad/s"),
            ManParm("ee_pause", Glider.inter.length, 20.0, "m"),
        ]
    ),
    dict(
        line=dict(
            func=line,
            args=[],
            kwargs=dict(
                speed=50,
                length=180,
            ),
        ),
        loop=dict(
            func=loopmaker,
            args=["angle"],
            kwargs=dict(
                speed=50,
                radius=130,
                rolls=0.0,
                ke=False,
                rollangle=None,
                rolltypes="roll",
                reversible=True,
                pause_length="point_length",
                break_angle=np.radians(10),
                snap_rate="snap_rate",
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
                speed=50,
                line_length=180,
                partial_rate="partial_roll_rate",
                full_rate="full_roll_rate",
                pause_length="point_length",
                mode="imac",
                break_angle=np.radians(10),
                snap_rate="snap_rate",
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
                speed=50,
                line_length=180,
                partial_rate="partial_roll_rate",
                full_rate="full_roll_rate",
                pause_length="point_length",
                mode="imac",
                break_angle=np.radians(10),
                snap_rate="snap_rate",
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
    Glider.inter,
    box
)
