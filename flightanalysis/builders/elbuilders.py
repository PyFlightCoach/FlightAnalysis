from flightanalysis.definition.eldef import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.elements import Line, Loop, StallTurn, Snap, Spin
from flightanalysis.definition.collectors import Collectors
from flightanalysis.definition import ItemOpp
from numbers import Number
import numpy as np


def line(name: str, speed, length, dggrps, Inter):
    return ElDef.build(
        Line,
        name,
        [speed, length],
        dggrps.line,
    ), ManParms()


def roll(name: str, speed, rate, rolls, dggrps, Inter):
    el = ElDef.build(
        Line,
        name,
        [speed, abs(rolls) * speed / rate, rolls],
        dggrps.roll,
    )
    if isinstance(rate, ManParm):
        rate.collectors.add(el.get_collector("rate"))
    return el, ManParms()


def loop(name: str, speed, radius, angle, ke, dggrps, Inter):
    ed = ElDef.build(
        Loop,
        name,
        [speed, angle, radius, 0, ke],
        dggrps.loop,
    )
    return ed, ManParms()


def rolling_loop(name, speed, radius, angle, roll, ke, dggrps, Inter):
    ed = ElDef.build(
        Loop,
        name,
        [speed, angle, radius, roll, ke],
        dggrps.rolling_loop,
    )
    return ed, ManParms()


def stallturn(name, speed, yaw_rate, dggrps, Inter):
    return ElDef.build(
        StallTurn,
        name,
        [speed, yaw_rate],
        dggrps.stallturn,
    ), ManParms()


def snap(name, rolls, break_angle, rate, speed, break_roll, recovery_roll, dggrps, Inter):
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
        ],
        dggrps.snap,
    )
    if isinstance(rate, ManParm):
        rate.collectors.add(ed.get_collector("rate"))
    return ed, ManParms()


def spin(name, turns, rate, break_angle, speed, nd_turns, recovery_turns, dggrps, Inter):
    height = Spin.get_height(speed, rate, turns, nd_turns, recovery_turns)
    ed = ElDef.build(
        Spin,
        name,
        [speed, height, turns, break_angle, nd_turns, recovery_turns],
        dggrps.spin,
    )

    if isinstance(rate, ManParm):
        rate.collectors.add(ed.get_collector("rate"))

    return ed, ManParms()


def parse_rolltypes(rolltypes, n):
    if rolltypes == "roll" or rolltypes is None:
        return "".join(["r" for _ in range(n)])
    elif rolltypes == "snap":
        return "".join(["s" for _ in range(n)])
    else:
        assert len(rolltypes) == len(range(n))
        return rolltypes


def roll_combo(
    name,
    speed,
    rolls,
    rolltypes,
    partial_rate,
    full_rate,
    pause_length,
    break_angle,
    snap_rate,
    break_roll,
    recovery_roll,
    mode,
    dggrps,
    Inter
) -> ElDefs:
    """This creates a set of ElDefs to represent a list of rolls or snaps
    and pauses between them if mode==f3a it does not create pauses when roll direction is reversed
    """
    eds = ElDefs()
    rolltypes = parse_rolltypes(rolltypes, len(rolls.value))

    for i, r in enumerate(rolls.value):
        if rolltypes[i] == "r":
            eds.add(
                roll(
                    f"{name}_{i}",
                    speed,
                    partial_rate if abs(r) < 2 * np.pi else full_rate,
                    rolls[i],
                    dggrps,
                    Inter
                )[0]
            )
        else:
            eds.add(
                snap(
                    f"{name}_{i}",
                    rolls[i],
                    break_angle,
                    snap_rate,
                    speed,
                    break_roll,
                    recovery_roll,
                    dggrps,
                    Inter
                )[0]
            )

        if i < rolls.n - 1 and (
            mode == "imac" or np.sign(r) == np.sign(rolls.value[i + 1])
        ):
            eds.add(line(f"{name}_{i+1}_pause", speed, pause_length, dggrps, Inter))

    return eds, ManParms()


def pad(speed, line_length, eds: ElDefs, dggrps, Inter):
    """This will add pads to the ends of the element definitions to
    make the total length equal to line_length"""
    eds = ElDefs([eds]) if isinstance(eds, ElDef) else eds

    pad_length = 0.5 * (line_length - eds.builder_sum("length"))

    e1 = line(f"e_{eds[0].id}_pad1", speed, pad_length, dggrps, Inter)[0]
    e3 = line(f"e_{eds[0].id}_pad2", speed, pad_length, dggrps, Inter)[0]

    mp = ManParm(
        f"e_{eds[0].id}_pad_length",
        Inter.length,
        None,
        "m",
        Collectors([e1.get_collector("length"), e3.get_collector("length")]),
    )

    eds = ElDefs([e1] + [ed for ed in eds] + [e3])

    if isinstance(line_length, ManParm):
        line_length.append(eds.collector_sum("length", f"e_{eds[0].id}"))

    return eds, ManParms([mp])


def rollmaker(
    name,
    rolls,
    rolltypes,
    speed,
    partial_rate,
    full_rate,
    pause_length,
    line_length,
    reversible,
    break_angle,
    snap_rate,
    break_roll,
    recovery_roll,
    padded,
    mode,
    dggrps,
    Inter
):
    """This will create a set of ElDefs to represent a series of rolls or snaps
    and pauses between them and the pads at the ends if padded==True.
    """
    mps = ManParms()

    _rolls = mps.parse_rolls(rolls, name, reversible)

    if isinstance(_rolls, ItemOpp):
        if rolltypes[0] == "r":
            _r = _rolls.a.value[_rolls.item]
            rate = full_rate if abs(_r) >= 2 * np.pi else partial_rate
            eds, rcmps = roll(f"{name}_roll", speed, rate, _rolls, dggrps, Inter)
        else:
            eds, rcmps = snap(
                f"{name}_snap",
                _rolls,
                break_angle,
                snap_rate,
                speed,
                break_roll,
                recovery_roll,
                dggrps,
                Inter
            )
    else:
        eds, rcmps = roll_combo(
            name,
            speed,
            _rolls,
            rolltypes,
            partial_rate,
            full_rate,
            pause_length,
            break_angle,
            snap_rate,
            break_roll,
            recovery_roll,
            mode,
            dggrps,
            Inter
        )

    mps.add(rcmps)

    if padded:
        eds, padmps = pad(speed, line_length, eds, dggrps, Inter)
        mps.add(padmps)

    return eds, mps


def loopmaker(
    name,
    speed,
    radius,
    angle,
    rolls,
    ke,
    rollangle,
    rolltypes,
    reversible,
    pause_length,
    break_angle,
    snap_rate,
    break_roll,
    recovery_roll,
    mode,
    dggrps,
    Inter
):
    """This will create a set of ElDefs to represent a series of loops and the pads at the ends if padded==True."""

    ke = 0 if not ke else np.pi / 2
    rollangle = angle if rollangle is None else rollangle

    if rolls == 0:
        return loop(name, speed, radius, angle, ke, dggrps, Inter)
    if (isinstance(rolls, Number) or isinstance(rolls, ItemOpp)) and rollangle == angle:
        return rolling_loop(name, speed, radius, angle, rolls, ke, dggrps, Inter)

    mps = ManParms()
    eds = ElDefs()

    rad = radius if isinstance(radius, Number) else radius.value

    internal_rad = ManParm(f"{name}_radius", Inter.free, rad, "m")

    rolls = mps.parse_rolls(rolls, name, reversible) if not rolls == 0 else 0

    try:
        rvs = rolls.value
    except Exception:
        rvs = None

    multi_rolls = rvs is not None
    rvs = [rolls] if rvs is None else rvs

    rolltypes = parse_rolltypes(rolltypes, len(rvs))

    angle = ManParm.parse(angle, mps)

    if not rollangle == angle:
        eds.add(
            loop(
                f"{name}_pad1", speed, internal_rad, (angle - rollangle) / 2, ke, dggrps, Inter
            )[0]
        )

    if multi_rolls:
        if mode == "f3a":
            has_pause = np.concatenate([np.diff(np.sign(rvs)), np.ones(1)]) == 0
        else:
            has_pause = np.concatenate([np.full(len(rvs) - 1, True), np.full(1, False)])

        pause_angle = pause_length / internal_rad

        if np.sum(has_pause) == 0:
            remaining_rollangle = rollangle
        else:
            remaining_rollangle = rollangle - pause_angle * np.sum(has_pause)

        only_rolls = []
        for i, rt in enumerate(rolltypes):
            only_rolls.append(abs(rvs[i]) if rt == "r" else 0)
        only_rolls = np.array(only_rolls)

        rolls.criteria.append_roll_sum(inplace=True)

        loop_proportions = np.abs(only_rolls) / np.sum(np.abs(only_rolls))

        loop_angles = [remaining_rollangle * rp for rp in loop_proportions]

        n = len(loop_angles)

        for i, r in enumerate(loop_angles):
            roll_done = rolls[i + n - 1] if i > 0 else 0
            if rolltypes[i] == "r":
                eds.add(
                    rolling_loop(
                        f"{name}_{i}",
                        speed,
                        internal_rad,
                        r,
                        rolls[i],
                        ke - roll_done,
                        dggrps, Inter
                    )[0]
                )
            else:
                ed, mps = snap(
                    f"{name}_{i}",
                    rolls[i],
                    break_angle,
                    snap_rate,
                    speed,
                    break_roll,
                    recovery_roll,
                    dggrps, Inter
                )
                eds.add(ed)
                snap_rate.collectors.add(eds[-2].get_collector("rate"))

            if has_pause[i]:
                eds.add(
                    loop(
                        f"{name}_{i}_pause",
                        speed,
                        internal_rad,
                        pause_angle,
                        ke - rolls[i + n],
                        dggrps, Inter
                    )[0]
                )

        ke = ke - rolls[i + n]

    else:
        eds.add(
            rolling_loop(
                f"{name}_rolls", speed, internal_rad, rollangle, rolls, ke, dggrps, Inter
            )[0]
        )
        ke = ke - rolls

    if not rollangle == angle:
        eds.add(
            loop(
                f"{name}_pad2", speed, internal_rad, (angle - rollangle) / 2, ke, dggrps, Inter
            )[0]
        )
    mps.add(internal_rad)
    return eds, mps
