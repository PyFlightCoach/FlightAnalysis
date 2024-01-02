from flightdata import State
from flightanalysis.scoring import Measurement
from geometry import Point, Quaternion, Transformation, PX, PY, PZ, Euldeg, P0, Q0
from pytest import fixture, approx
import numpy as np
from flightanalysis import Loop

@fixture
def line_tp():
    return State.from_transform(vel=PX(30)).extrapolate(2)


@fixture
def loop_tp():
    return Loop(30, 50, np.pi*3/2, 0).create_template(State.from_transform()) 

@fixture
def keloop_tp():
    return Loop(30, 50, np.pi*3/2, 0, ke=True).create_template(State.from_transform()) 



@fixture
def ke45loop_tp():
    return Loop(30, 50, np.pi*3/2, 0, ke=np.pi/4).create_template(State.from_transform()) 


def track_setup(tp: State, cerror: Quaternion):
    cfl = tp.move(tp[0].back_transform).move(Transformation(P0(), cerror))
    return cfl.move(tp[0].transform)
    
    
def test_track_y_line(line_tp: State):
    tp = line_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = track_setup(tp, Euldeg(0, 0, 10))

    m = Measurement.track_y(fl, tp, tp[0].transform)

    np.testing.assert_array_almost_equal(np.degrees(abs(m.value)), np.full(len(m.value), 10.0))

def test_track_y_loop(loop_tp: State):
    tp = loop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = track_setup(tp, Euldeg(0, 0, 10))
    m = Measurement.track_y(fl, tp, tp[0].transform)
    np.testing.assert_array_almost_equal(np.degrees(abs(m.value)), np.full(len(m.value), 0.0))
    
    
def test_roll_angle_loop(loop_tp: State):
    tp = loop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = tp.superimpose_roll(np.radians(5))
    m = Measurement.roll_angle_proj(fl, tp, tp[0].transform, PY())
    assert np.degrees(m.value[-1]) == approx(5)
    
def test_roll_angle_ke_loop(keloop_tp: State):
    tp = keloop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = tp.superimpose_roll(np.radians(5))
    m = Measurement.roll_angle_proj(fl, tp, tp[0].transform, PZ())
    assert np.degrees(m.value[-1]) == approx(5)
    
    
def test_roll_angle_45_loop(ke45loop_tp: State):
    tp = ke45loop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = tp.superimpose_roll(np.radians(-5))
    m = Measurement.roll_angle_proj(fl, tp, tp[0].transform, Point(0,1,1).unit())
    assert np.degrees(m.value[-1]) == approx(-5)
    
    
    
def test_wingspans():
    pass