from numbers import Number

import numpy as np

from flightanalysis.definition import ItemOpp, Opp, maxopp
from flightanalysis.definition.collectors import Collectors
from flightanalysis.definition.eldef import ElDef, ElDefs, ManParm, ManParms
from flightanalysis.elements import Line, Loop, Snap, Spin, StallTurn, TailSlide
from flightanalysis.scoring import visor
from flightanalysis.scoring.criteria.inter.comparison import free_comparison


def line(name: str, speed, length, Inter):
    return ElDef.build(Line, name, [speed, length]), ManParms()


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
    ed = ElDef.build(Loop, name, [speed, angle, radius, roll, ke])
    return ed, ManParms()


def stallturn(name, speed, yaw_rate, Inter):
    return ElDef.build(StallTurn, name, [speed, yaw_rate]), ManParms()


def tailslide(name, speed, direction, rate, over_flop, reset_rate, Inter):
    return ElDef.build(
        TailSlide, name, [speed, abs(rate) * direction, over_flop, reset_rate]
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
        ],
    )
    if isinstance(rate, ManParm):
        rate.collectors.add(ed.get_collector("rate"))
    return ed, ManParms()


def spin(name, turns, rate, break_angle, speed, nd_turns, recovery_turns, Inter):
    height = Spin.get_height(speed, rate, turns, nd_turns, recovery_turns)
    ed = ElDef.build(
        Spin, name, [speed, height, turns, break_angle, nd_turns, recovery_turns]
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
    Inter,
) -> ElDefs:
    """This creates a set of ElDefs to represent a list of rolls or snaps
    and pauses between them if mode==f3a it does not create pauses when roll direction is reversed
    """
    eds = ElDefs()

    rvs = [r.a.value[r.item] for r in rolls] if isinstance(rolls, list) else rolls.value

    rolltypes = parse_rolltypes(rolltypes, len(rvs))

    for i, r in enumerate(rvs):
        if rolltypes[i] == "r":
            eds.add(
                roll(
                    f"{name}_{i}",
                    speed,
                    partial_rate if abs(r) < 2 * np.pi else full_rate,
                    rolls[i],
                    Inter,
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
                    Inter,
                )[0]
            )

        if i < len(rvs) - 1 and (mode == "imac" or np.sign(r) == np.sign(rvs[i + 1])):
            eds.add(line(f"{name}_{i + 1}_pause", speed, pause_length, Inter))

    return eds, ManParms()


def pad(speed, line_length, eds: ElDefs, Inter):
    """This will add pads to the ends of the element definitions to
    make the total length equal to line_length"""
    eds = ElDefs([eds]) if isinstance(eds, ElDef) else eds

    pad_length = maxopp(
        "min_pad_length", 0.5 * (line_length - eds.builder_sum("length")), 20
    )

    e1 = line(f"e_{eds[0].id}_pad1", speed, pad_length, Inter)[0]
    e3 = line(f"e_{eds[0].id}_pad2", speed, pad_length, Inter)[0]

    mp = ManParm(
        f"e_{eds[0].id}_pad_length",
        Inter.length if hasattr(Inter, "length") else free_comparison,
        None,
        "m",
        Collectors([e1.get_collector("length"), e3.get_collector("length")]),
        visor.scale()
        if "scale" in visor.funcs
        else lambda fl, *args, **kwargs: np.ones(len(fl)),
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
    Inter,
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
            eds, rcmps = roll(f"{name}_roll", speed, rate, _rolls, Inter)
        else:
            eds, rcmps = snap(
                f"{name}_snap",
                _rolls,
                break_angle,
                snap_rate,
                speed,
                break_roll,
                recovery_roll,
                Inter,
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
            Inter,
        )

    mps.add(rcmps)

    if padded:
        eds, padmps = pad(speed, line_length, eds, Inter)
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
    rollposition,
    rolltypes,
    reversible,
    pause_length,
    break_angle,
    snap_rate,
    break_roll,
    recovery_roll,
    mode,
    Inter,
):
    """Create a set of ElDefs to represent a loops with integrated rolls"""
    if isinstance(ke, bool):
        ke = 0 if not ke else np.pi / 2
    sign = angle.sign() if isinstance(angle, Opp) else np.sign(angle)
    rollangle = angle if rollangle is None else rollangle * sign

    mps = ManParms()
    rolls = mps.parse_rolls(rolls, name, reversible) if not rolls == 0 else 0
    if isinstance(rolls, ManParm) and len(rolls.value) == 1:
        rolls = rolls[0]
    if rolls == 0:
        return loop(name, speed, radius, angle, ke, Inter)
    if isinstance(rolls, ItemOpp) and rollangle == angle:
        ed = rolling_loop(name, speed, radius, angle, rolls, ke, Inter)[0]
        return ed, mps

    eds = ElDefs()

    rad = radius if isinstance(radius, Number) else radius.value

    internal_rad = ManParm(f"{name}_radius", free_comparison, rad, "m")

    try:
        rvs = rolls.value
    except Exception:
        rvs = None

    multi_rolls = rvs is not None
    rvs = [rolls] if rvs is None else rvs

    rolltypes = parse_rolltypes(rolltypes, len(rvs))

    if all([r == "s" for r in rolltypes]):
        rollangle = 0

    angle = ManParm.parse(angle, mps)

    if not rollangle == angle:
        eds.add(
            loop(
                f"{name}_pad1",
                speed,
                internal_rad,
                sign * (abs(angle) * rollposition - abs(rollangle) / 2),
                ke,
                Inter,
            )[0]
        )

    if multi_rolls:
        if mode == "f3a":
            has_pause = np.concatenate([np.diff(np.sign(rvs)), np.ones(1)]) == 0
        else:
            has_pause = np.concatenate([np.full(len(rvs) - 1, True), np.full(1, False)])

        pause_angle = sign * pause_length / internal_rad

        if np.sum(has_pause) == 0:
            remaining_rollangle = rollangle
        else:
            remaining_rollangle = sign * (
                abs(rollangle) - abs(pause_angle) * np.sum(has_pause)
            )

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
                        Inter,
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
                        Inter,
                    )[0]
                )
                if isinstance(snap_rate, ManParm):
                    snap_rate.collectors.add(eds[-2].get_collector("rate"))

            if has_pause[i]:
                eds.add(
                    loop(
                        f"{name}_{i}_pause",
                        speed,
                        internal_rad,
                        pause_angle,
                        ke - rolls[i + n],
                        Inter,
                    )[0]
                )

        ke = ke - rolls[i + n]

    else:
        if rolltypes == "s":
            eds.add(
                snap(
                    f"{name}_0",
                    rolls,
                    break_angle,
                    snap_rate,
                    speed,
                    break_roll,
                    recovery_roll,
                    Inter,
                )[0]
            )

        else:
            eds.add(
                rolling_loop(
                    f"{name}_0", speed, internal_rad, rollangle, rolls, ke, Inter
                )[0]
            )
        ke = ke - rolls

    if not rollangle == angle:
        eds.add(
            loop(
                f"{name}_pad2",
                speed,
                internal_rad,
                sign * (abs(angle) * (1 - rollposition) - abs(rollangle) / 2),
                ke,
                Inter,
            )[0]
        )
    mps.add(internal_rad)
    return eds, mps
