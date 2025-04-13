
from flightanalysis.elements import Loop, Line, Snap, Spin, StallTurn, TailSlide
from flightanalysis.scoring.downgrade import DownGrades
from flightdata import State


def dg_applicator(el: Loop | Line | Snap | Spin | StallTurn | TailSlide, tp: State, last_kind: str, next_kind: str):
    """PLaceholder for a function to assign intra element downgrades to an element"""
    match el.__class__.__name__:
        case "Loop":
            pass
        case "Line":
            pass
        case "Snap": 
            pass
        case "Spin":
            pass
        case "StallTurn":
            pass
        case "TailSlide":
            pass
    return DownGrades()