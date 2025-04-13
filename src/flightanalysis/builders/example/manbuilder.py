import numpy as np

from flightanalysis.builders.example.box import box
from flightanalysis.builders.example.criteria import InterCrit
from flightanalysis.builders.example.downgrades import dg_applicator
from flightanalysis.builders.elbuilders import (
    line,
    loopmaker,
    rollmaker,
    spin,
    stallturn,
    tailslide
)
from flightanalysis.builders.manbuilder import ManBuilder
from flightanalysis.definition import ManParms


mb = ManBuilder(
    ManParms(),
    dict(
        line=dict(
            func=line,
            args=[],
            kwargs=dict(
                speed=40,
                length=150,
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
                rollposition=0.5,
                rolltypes="roll",
                reversible=True,
                pause_length=30,
                break_angle=np.radians(10),
                snap_rate=3 * np.pi,
                break_roll=np.pi / 4,
                recovery_roll=np.pi / 2,
                mode="f3a",
            ),
        ),
        roll=dict(
            func=rollmaker,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed=40,
                line_length=150,
                partial_rate=np.pi/2,
                full_rate=np.pi/2,
                pause_length=30,
                mode="f3a",
                break_angle=np.radians(10),
                snap_rate=3 * np.pi,
                break_roll=np.pi / 4,
                recovery_roll=np.pi / 2,
                rolltypes="roll",
            ),
        ),
        stallturn=dict(
            func=stallturn, args=[], kwargs=dict(speed=0.0, yaw_rate=np.pi)
        ),
        snap=dict(
            func=rollmaker,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed=40,
                line_length=150,
                partial_rate=np.pi/2,
                full_rate=np.pi/2,
                pause_length=30,
                mode="f3a",
                break_angle=np.radians(10),
                snap_rate=3*np.pi,
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
                rate=1.7 * np.pi,
                nd_turns=np.pi / 4,
                recovery_turns=np.pi / 2,
            ),
        ),
        tailslide=dict(
            func=tailslide,
            args=[],
            kwargs=dict(
                speed=-5.0,
                direction=1,
                rate=np.pi,
                over_flop=np.radians(30),
                reset_rate=np.pi,
            ),
        ),
    ),
    dg_applicator,
    InterCrit,
    box
)
