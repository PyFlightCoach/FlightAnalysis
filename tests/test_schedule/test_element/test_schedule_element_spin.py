from flightanalysis.elements import Spin
from geometry import Transformation, Euler, P0, PX, PY, PZ, Point, Quaternion
import numpy as np
from flightdata import State
from pytest import fixture, approx
from plotting import plotsec
import plotly.express as px

@fixture
def el():
    return Spin('spin', 10, 25, 2*np.pi, np.radians(30), np.pi/2, np.pi/4)

@fixture
def tp(el: Spin):
    return el.create_template(
        State.from_transform(Transformation(Euler(np.pi, 0, 0)))
    )



def test_create_template(el: Spin, tp: State):
    plotsec(tp, nmodels=5, scale=1).show()
    
    px.line(tp.rvel).show()
    np.testing.assert_array_almost_equal(
        tp[-1].att.transform_point(PY()).data,
        tp[0].att.transform_point(PY()).data
    ) 
    assert abs(tp.pos[-1].z - tp.pos[0].z)[0] == approx(el.height)

def test_match_intention(sn, snt):
    sn2 = Snap('snap', 30, 50, -2*np.pi, -np.radians(20), np.pi/4, np.pi/4)


    sn3 = sn2.match_intention(Transformation(), snt)

    assert sn.speed == approx(sn3.speed)
    assert sn.length == approx(sn3.length)
    assert sn.roll == approx(sn3.roll)
    assert sn.pitch == approx(sn3.pitch)

