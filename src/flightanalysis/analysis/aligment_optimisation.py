import numpy as np
from flightanalysis.scoring.results import Results
from flightanalysis.definition import ElDef, ManDef
from flightanalysis.elements import AnyElement, Elements
from flightanalysis.manoeuvre import Manoeuvre
from flightdata import State
import geometry as g
from loguru import logger


def get_score(
    ed: ElDef, el: AnyElement, itrans: g.Transformation, fl: State
) -> tuple[Results, g.Transformation]:
    el: AnyElement = el.match_intention(itrans, fl)
    tp = el.create_template(State.from_transform(itrans), fl)
    return ed.dgs.apply(el, fl, tp, False), el, tp  # tp[-1].att


def _optimise_split(
    mdef: ManDef,
    manoeuvre: Manoeuvre,
    templates: dict[str, State],
    eln1: str,
    eln2: str,
    itrans: g.Transformation,
    fl: State,
    min_len: int = 3,
) -> int:
    def score_split(steps: int) -> float:
        new_fl = fl.step_label("element", eln1, steps, fl.t, min_len)
        res1, oel1, tp1 = get_score(
            mdef.eds[eln1], manoeuvre.elements[eln1], itrans, getattr(new_fl.element, eln1)
        )

        el2fl = getattr(new_fl.element, eln2)
        res2, oel2, tp2 = get_score(
            mdef.eds[eln2], manoeuvre.elements[eln2], g.Transformation(tp1[-1].att, el2fl[0].pos), el2fl
        )

        oman = Manoeuvre.from_all_elements(
            manoeuvre.uid,
            Elements(manoeuvre.elements.data | {oel1.uid: oel1, oel2.uid: oel2}),
        )

        omdef = mdef.update_defaults(oman)

        inter = omdef.mps.collect(
            oman,
            State.stack(templates | {oel1.uid: tp1, oel2.uid: tp2}, "element"),
            mdef.box,
        )

        logger.debug(f"split {steps} {res1.total + res2.total:.2f}")
        logger.debug(
            f"e1={oel1.uid}, e2={oel2.uid}, steps={steps}, intra={res1.total + res2.total:.2f}, inter={inter.total}"
        )
        return res1.total + res2.total + inter.total

    dgs = {0: score_split(0)}

    def check_steps(stps: int):
        new_l2 = len(getattr(fl.element, eln2)) - stps + 1
        new_l1 = len(getattr(fl.element, eln1)) + stps + 1
        return new_l2 > min_len and new_l1 > min_len

    steps = int(len(getattr(fl.element, eln1)) > len(getattr(fl.element, eln2))) * 2 - 1

    if not check_steps(steps):
        return 0

    try:
        new_dg = score_split(steps)
        if new_dg > dgs[0]:
            steps = -steps
        else:
            dgs[steps] = new_dg
            steps += np.sign(steps)
    except Exception:
        steps = -steps

    while check_steps(steps):
        try:
            new_dg = score_split(steps)
            if new_dg < list(dgs.values())[-1]:
                dgs[steps] = new_dg
                steps += np.sign(steps)
            else:
                break
        except ValueError:
            break

    min_dg_step = np.argmin(np.array(list(dgs.values())))
    out_steps = list(dgs.keys())[min_dg_step]
    return out_steps


def optimise_alignment(
    flown: State, mdef: ManDef, manoeuvre: Manoeuvre, templates: dict[str, State]
) -> State:
    elns = list(mdef.eds.data.keys())

    padjusted = set(elns)
    count = 0
    while len(padjusted) > 0 and count < 2:
        adjusted = set()
        for eln1, eln2 in zip(elns[:-1], elns[1:]):
            if (eln1 in padjusted) or (eln2 in padjusted):
                itrans = g.Transformation(
                    templates[eln1][0].att,
                    flown.element[eln1][0].pos,
                )
                steps = _optimise_split(
                    mdef,
                    manoeuvre,
                    templates,
                    eln1,  # flown.element[eln1][0],
                    eln2,  # flown.element[eln2][0],
                    itrans,
                    flown,
                )

                if not steps == 0:
                    logger.debug(
                        f"Adjusting split between {eln1} and {eln2} by {steps} steps"
                    )
                    flown = flown.step_label("element", eln1, steps, flown.t, 3)
                    adjusted.update([eln1, eln2])

        padjusted = adjusted
        count += 1
        logger.debug(f"pass {count}, {len(padjusted)} elements adjusted:\n{padjusted}")

    return flown
