

from flightanalysis import Loop, Element, ElementAnalysis
from pytest import approx, fixture, mark
from flightdata import State
from geometry import Transformation, Point, PX, Euler, P0, Time
import numpy as np
from geometry.checks import assert_almost_equal
import json 


@fixture
def half_loop():
    return Loop("loop", 30, np.pi, 50.0, 0, 0)

@fixture
def hl_template(half_loop: Loop):
    return half_loop.create_template(State.from_transform(vel=PX(30)))


def test_create_template_no_t(half_loop, hl_template):
    assert_almost_equal(
        hl_template[-1].att.transform_point(PX(1)),
        PX(-1)
    )

    assert_almost_equal(
        hl_template[-1].pos,
        Point(0, 0, -half_loop.diameter),
        2
    )


def test_create_template_itrans(half_loop):
    tp = half_loop.create_template(State.from_transform(Transformation(Euler(0, 0, 0)), vel=PX(30)))
    assert tp[-1].pos.z == approx(-half_loop.diameter, abs=1e-3)
    assert tp[tp.duration/2].pos.x == approx(half_loop.diameter/2, abs=1e-3)

    tp = half_loop.create_template(State.from_transform(Transformation(Euler(0, 0, np.pi)), vel=PX(30)))
    assert tp[-1].pos.z == approx(-half_loop.diameter, abs=1e-3)
    assert tp[tp.duration/2].pos.x == approx(-half_loop.diameter/2, abs=1e-3)


def test_create_template_ke_angles():
    istate = State.from_transform(Transformation(Euler(np.pi, 0, 0)))
    tp = Loop("loop", 30, np.pi/2, 100, 0, 0).create_template(istate)
    assert_almost_equal(tp.pos[-1], Point(100, 0, 100), 0)
    tp = Loop("loop", 30, np.pi/2, 100, 0, np.pi/2).create_template(istate)
    assert_almost_equal(tp.pos[-1], Point(100, -100, 0), 0)


def test_match_intention():

    el = Loop("loop", 30, np.radians(180), 100, 0, 0)

    tp = el.create_template(State.from_transform(Transformation(),vel=PX(30))) 
    
    att = Euler(0, np.radians(20), 0)

    fl = el.create_template(State.from_transform(
        Transformation(P0(), att),
        vel=att.inverse().transform_point(PX(30))
    ))

    el_diff = Loop("loop", 20, np.radians(180), 50, -np.pi, 0)


    el2 = el_diff.match_intention(tp[0].transform, fl)
    assert el2.radius == approx(el.radius, rel=0.01)

def test_match_intention_ke():

    el = Loop("loop", 30, np.radians(180), 100, 0, 0)

    tp = el.create_template(State.from_transform(Transformation(),vel=PX(30))) 

    att = Euler(0, np.radians(20), 0)

    fl = el.create_template(State.from_transform(
        Transformation(P0(), att),
        vel=att.inverse().transform_point(PX(30))
    ))

    el_diff = Loop("loop", 20, np.radians(180), 50, -np.pi, 0)


    el2 = el_diff.match_intention(tp[0].transform, fl)

    assert el.radius == approx(el2.radius, rel=0.01)
    assert el.roll == approx(el2.roll)
    assert el.speed == approx(el2.speed)
    assert el.uid == el2.uid
    
    


@fixture
def th_e0()->State:
    return State.from_csv("tests/test_schedule/test_element/p23_th_e0.csv")

@fixture
def th_el()->Loop:
    with open("tests/test_schedule/test_element/p23_th_e0.json", "r") as f:
        return Element.from_dict(json.load(f))

@fixture
def th_e0_tp()->State:
    return State.from_csv("tests/test_schedule/test_element/p23_th_e0_template.csv")



@fixture
def ql():
    return Loop("loop", 30,np.pi/2, 100, 0, 0)

@fixture
def ql_tp(ql):
    return ql.create_template(Transformation.zero())


@fixture
def ql_fl():
    return Loop(
        "loop",
        30, 
        np.pi/2 - np.radians(10), 
        100, 
        0, 0
    ).create_template(Transformation.zero())

@mark.skip
def test_intra_scoring(ql, ql_tp, ql_fl):
    ql_fl = ql.setup_analysis_state(ql_fl, ql_tp)
    ql_tp = ql.setup_analysis_state(ql_tp, ql_tp)
    dgs = ql.intra_scoring.apply(ql, ql_fl, ql_tp)

    pass


def test_serialization(half_loop):
    dhl = half_loop.to_dict()
    hl = Element.from_dict(dhl)

    assert half_loop == hl


def test_create_template_new_time(half_loop: Loop, hl_template):
    tp = half_loop.create_template(
        State.from_transform(Transformation(), vel=PX(30)), 
        hl_template
    )
    
    assert sum((tp.q * tp.dt)[:-1]) == approx(np.pi, abs=1e-3)
    assert len(tp) == len(hl_template)
    
