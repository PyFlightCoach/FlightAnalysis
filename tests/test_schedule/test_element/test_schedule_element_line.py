

from flightanalysis.elements import Line
import geometry as g
import numpy as np
from pytest import approx
from flightdata import State


def test_create_template():
    template = Line('line', 30, 100).create_template(State.from_transform(g.Transformation(),vel=g.PX(30)))
    
    np.testing.assert_array_almost_equal(
        template[-1].pos.data,
        g.PX(100).data,
        0
    )
  

def test_match_intention():
    # a line
    el = Line("test", 30, 100, np.radians(180))

    # a template State
    tp = el.create_template(State.from_transform(g.Transformation(),vel=g.PX(30)))

    # some alpha
    att = g.Euler(0, np.radians(20), 0)

    # a flown State
    fl = el.create_template(
        State.from_transform(
            g.Transformation(g.P0(), att),
            vel=att.inverse().transform_point(g.PX(30))
    ))

    # a slightly different line
    el2 = Line("test", 15, 200, -np.radians(180))

    #match intention should make it the same as the first line
    el3 = el2.match_intention(tp[0].transform, fl)
    assert el3.length == approx(el.length)
    assert el3.roll == approx(el.roll)
    assert el3.speed == approx(el.speed)
    assert el3.uid == el.uid
    

