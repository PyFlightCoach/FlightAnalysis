from flightanalysis.elements import Snap
import geometry as g
import numpy as np
from flightdata import State
from pytest import fixture, approx
from plotting import plotsec


@fixture
def sn():
    return Snap('snap', 30, 30, 2*np.pi, np.radians(20), np.pi/4, np.pi/4)

@fixture
def snt(sn: Snap):
    return sn.create_template(
        State.from_transform(g.Transformation(g.Euler(np.pi, 0, 0)))
    )



def test_create_template(sn: Snap, snt: State):
    #plotsec(snt, nmodels=5, scale=1).show()
    
    
    np.testing.assert_array_almost_equal(
        snt[-1].att.transform_point(g.PY()).data,
        snt[0].att.transform_point(g.PY()).data
    ) 
    assert abs(snt.pos[-1] - snt.pos[0])[0] == approx(sn.length)

def test_match_intention(sn, snt):
    sn2 = Snap('snap', 30, 50, -2*np.pi, -np.radians(20), np.pi/4, np.pi/4)


    sn3 = sn2.match_intention(g.Transformation(), snt)

    assert sn.speed == approx(sn3.speed)
    assert sn.length == approx(sn3.length)
    assert sn.roll == approx(sn3.roll)
    assert sn.pitch == approx(sn3.pitch)

