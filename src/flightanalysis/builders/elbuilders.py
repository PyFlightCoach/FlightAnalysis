from flightanalysis.definition.eldef import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.elements import Line, Loop, StallTurn, Snap, Spin
from flightanalysis.definition.collectors import Collectors
from flightanalysis.definition import ItemOpp, Opp
from numbers import Number
import numpy as np


def line(name: str, speed, length, Inter):
    return ElDef.build(
        Line,
        name,
        [speed, length]
    ), ManParms()


def roll(name: str, speed, rate, rolls, Inter):
    el = ElDef.build(
        Line,
        name,
        [speed, abs(rolls) * speed / rate, rolls],
    )
    if isinstance(rate, ManParm):
        rate.collectors.add(el.get_collector("rate"))
    return el, ManParms()


def loop(name: str, speed, radius, angle, ke, Inter):
    ed = ElDef.build(
        Loop,
        name,
        [speed, angle, radius, 0, ke],
    )
    return ed, ManParms()


def rolling_loop(name, speed, radius, angle, roll, ke, Inter):
    ed = ElDef.build(
        Loop,
        name,
        [speed, angle, radius, roll, ke]
    )
    return ed, ManParms()


def stallturn(name, speed, yaw_rate, Inter):
    return ElDef.build(
        StallTurn,
        name,
        [speed, yaw_rate]
    ), ManParms()


def snap(name, rolls, break_angle, rate, speed, break_roll, recovery_roll, Inter):
    ed = ElDef.build(
        Snap,
        name,
        [
            speed,
            speed * abs(rolls) / rate,
            rolls,
            break_angle,
            break_roll,
            recovery_roll,
        ]
    )
    if isinstance(rate, ManParm):
        rate.collectors.add(ed.get_collector("rate"))
    return ed, ManParms()


def spin(name, turns, rate, break_angle, speed, nd_turns, recovery_turns, Inter):
    height = Spin.get_height(speed, rate, turns, nd_turns, recovery_turns)
    ed = ElDef.build(
        Spin,
        name,
        [speed, height, turns, break_angle, nd_turns, recovery_turns]
    )

    if isinstance(rate, ManParm):
        rate.collectors.add(ed.get_collector("rate"))

    return ed, ManParms()
