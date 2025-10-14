from flightanalysis.elements import Spin, Snap
import geometry as g
import numpy as np
from flightdata import State
from pytest import fixture, approx

@fixture
def el():
    return Spin('spin', 10, 25, 2*np.pi, np.radians(30), np.pi/2, np.pi/4)

@fixture
def tp(el: Spin):
    return el.create_template(
        State.from_transform(g.Transformation(g.Euler(np.pi, 0, 0), vel=g.PX(10)))
    )



def test_create_template(el: Spin, tp: State):    
    np.testing.assert_array_almost_equal(
        tp[-1].att.transform_point(g.PY()).data,
        tp[0].att.transform_point(g.PY()).data
    ) 
    assert abs(tp.pos[-1].z - tp.pos[0].z)[0] == approx(el.height, 0.01)

