from enum import Enum, auto

import geometry as g
from flightanalysis import Elements,Spin,StallTurn,TailSlide
from flightdata import State


class ElTag(Enum):
    LINE = auto()
    LOOP = auto()
    SNAP = auto()
    SPIN = auto()
    STALLTURN = auto()
    TAILSLIDE = auto()
    ROLL = auto()
    ENTRYLINE = auto()
    EXITLINE = auto()
    PRESPIN = auto()
    POSTSPIN = auto()
    PRESTALLTURN = auto()
    POSTSTALLTURN = auto()
    PRETAILSLIDE = auto()
    POSTTAILSLIDE = auto()
    HORIZONTAL = auto()
    HORIZONTALENTRY = auto()
    HORIZONTALEXIT = auto()
    VERTICAL = auto()
    VERTICALENTRY = auto()
    VERTICALEXIT = auto()


def tag_elements(els: Elements, tps: dict[str, State]):
    tags = {}

    for i, this in enumerate(els):
        last = els[i - 1] if i else None
        next = els[i + 1] if i + 1 < len(els) else None
        tp = tps[this.uid]

        tag = [getattr(ElTag, this.__class__.__name__.upper())]

        if last is None:
            tag.append(ElTag.ENTRYLINE)
        elif next is None:
            tag.append(ElTag.EXITLINE)

        if hasattr(this, "roll") and abs(this.roll) > 0:
            tag.append(ElTag.ROLL)

        if next is StallTurn:
            tag.append(ElTag.PRESTALLTURN)
        elif last is StallTurn:
            tag.append(ElTag.POSTSTALLTURN)
        elif next is Spin:
            tag.append(ElTag.PRESPIN)
        elif last is Spin:
            tag.append(ElTag.POSTSPIN)
        elif next is TailSlide:
            tag.append(ElTag.PRETAILSLIDE)
        elif last is TailSlide:
            tag.append(ElTag.POSTTAILSLIDE)

        if all(g.point.is_either_parallel(tp.wvel, g.PZ())):
            tag.append(ElTag.VERTICAL)
        elif all(g.point.is_perpendicular(tp.wvel, g.PZ())):
            tag.append(ElTag.HORIZONTAL)
        else:
            if g.point.is_either_parallel(tp[0].wvel, g.PZ())[0]:
                tag.append(ElTag.VERTICALENTRY)
            elif g.point.is_perpendicular(tp[0].wvel, g.PZ())[0]:
                tag.append(ElTag.HORIZONTALENTRY)

            if g.point.is_either_parallel(tp[-1].wvel, g.PZ())[0]:
                tag.append(ElTag.VERTICALEXIT)
            elif g.point.is_perpendicular(tp[-1].wvel, g.PZ())[0]:
                tag.append(ElTag.HORIZONTALEXIT)

        tags[this.uid] = set(tag)

    return tags


def checktag(
    tag: set[ElTag], has: set[ElTag] = None, hasnot: set[ElTag] = None
) -> bool:
    if has is None:
        has = set()
    if hasnot is None:
        hasnot = set()
    return all(t in tag for t in has) and not any(t in tag for t in hasnot)


def checktagstring(tag: set[ElTag], tagstr: str) -> bool:
    has = []
    hasnot = []
    for checkstr in [s.strip() for s in tagstr.split(",")]:
        if checkstr.startswith("!"):
            hasnot.append(ElTag[checkstr[1:].upper()])
        else:
            has.append(ElTag[checkstr.upper()])

    return checktag(tag, has=set(has), hasnot=set(hasnot))
