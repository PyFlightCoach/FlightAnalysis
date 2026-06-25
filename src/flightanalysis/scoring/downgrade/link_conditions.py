from typing import Callable, TypeVar, Type, cast

import geometry as g
from flightdata.state import State

from flightanalysis.elements import Line, Loop, AnyElement


E1 = TypeVar("E1", bound=AnyElement)
E2 = TypeVar("E2", bound=AnyElement)

type Condition = Callable[[AnyElement, State, AnyElement, State], bool]

conditions: dict[str, Condition] = {}


def condition(fun: Condition) -> Condition:
    conditions[fun.__name__] = fun
    return fun


@condition
def identical_axes(el1: Loop, tp1: State, el2: Loop, tp2: State) -> bool:
    """
    Compares two loop elements and returns true if their axes are identical (parallel and same centre point)
    """
    axis_1 = tp1[0].att.transform_point(el1.axis)
    axis_2 = tp2[0].att.transform_point(el2.axis)
    return g.point.is_either_parallel(axis_1, axis_2) and (
        abs(tp1[0].body_to_world(el1.centre) - tp2[0].body_to_world(el2.centre))[0] < 1
    )


@condition
def zero_roll(el1: Loop | Line, tp1: State, el2: Loop | Line, tp2: State) -> bool:
    """
    Returns true if both roll values are zero
    """

    return ((not hasattr(el1, "roll")) or el1.roll == 0) and ((not hasattr(el2, "roll")) or el2.roll == 0)


@condition
def zero_roll2(el1: Loop | Line, tp1: State, el2: Loop | Line, tp2: State) -> bool:
    """
    return true if the second element has zero roll, regardless of the first element's roll value
    """
    return ((not hasattr(el2, "roll")) or el2.roll == 0)


@condition
def parallel_z(el1: Loop | Line, tp1: State, el2: Loop | Line, tp2: State) -> bool:
    """
    Compares a loop element to a line element and returns true if the line track z downgrade can
    link to the loop axial track downgrade.
    This means the line ref frame z axis needs to be parallel to loop axis
    """
    return parallel_axis(el1, tp1, el2, tp2, g.PZ())


@condition
def parallel_y(el1: Loop | Line, tp1: State, el2: Loop | Line, tp2: State) -> bool:
    """
    Compares a loop element to a line element and returns true if the line track y downgrade can
    link to the loop axial track downgrade.
    This means the line ref frame y axis needs to be parallel to loop axis
    """
    return parallel_axis(el1, tp1, el2, tp2, g.PY())


def parallel_axis(
    el1: Loop | Line, tp1: State, el2: Loop | Line, tp2: State, axis
) -> bool:
    loop_el, loop_tp, line_el, line_tp = identify_elements(
        el1, tp1, el2, tp2, Loop, Line
    )
    loop_axis = loop_tp[0].att.transform_point(loop_el.axis())
    line_axis = line_tp[0].att.transform_point(axis)

    return g.point.is_either_parallel(line_axis, loop_axis)


def identify_elements(
    el1: AnyElement,
    tp1: State,
    el2: AnyElement,
    tp2: State,
    e1_kind: Type[E1],
    e2_kind: Type[E2],
) -> tuple[E1, State, E2, State]:
    assert (isinstance(el1, e1_kind) and isinstance(el2, e2_kind)) or (
        isinstance(el1, e2_kind) and isinstance(el2, e1_kind)
    )
    if isinstance(el1, e1_kind):
        return cast(tuple[E1, State, E2, State], (el1, tp1, el2, tp2))
    return cast(tuple[E1, State, E2, State], (el2, tp2, el1, tp1))
