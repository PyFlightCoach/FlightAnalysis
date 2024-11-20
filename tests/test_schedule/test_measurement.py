from flightdata import State
from geometry import Point, Quaternion, Transformation, PX, PY, PZ, Euldeg, P0
from pytest import fixture, approx
import numpy as np
from flightanalysis import Loop, Measurement
from flightanalysis.builders.manbuilder import r
from example.downgrades import dg_applicator
from geometry.checks import assert_almost_equal

@fixture
def line_tp():
    return State.from_transform(vel=PX(30)).extrapolate(2)


@fixture
def loop_tp():
    return Loop('loop', 30, np.pi*3/2, 50, 0, 0).create_template(State.from_transform()) 

@fixture
def keloop_tp():
    return Loop('keloop', 30, np.pi*3/2, 50, 0, np.pi/2).create_template(State.from_transform()) 

@fixture
def ke45loop_tp():
    return Loop('ke45lp', 30, np.pi*3/2, 50, 0, ke=np.pi/4).create_template(State.from_transform()) 

def track_setup(tp: State, cerror: Quaternion):
    cfl = tp.move(tp[0].back_transform).move(Transformation(P0(), cerror))
    return cfl.move(tp[0].transform)
    
    
def test_track_y_line(line_tp: State):
    tp = line_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = track_setup(tp, Euldeg(0, 0, 10))

    m = Measurement.track_y(fl, tp)

    np.testing.assert_array_almost_equal(np.degrees(abs(m.value)), np.full(len(m.value), 10.0))

def test_track_y_loop(loop_tp: State):
    tp = loop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = track_setup(tp, Euldeg(0, 0, 10))
    m = Measurement.track_y(fl, tp)
    assert m.value == approx(np.zeros_like(m.value), abs=0.2)



    
    
def test_roll_angle_loop(loop_tp: State):
    tp = loop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = tp.superimpose_roll(np.radians(5))
    m = Measurement.roll_angle_proj(fl, tp, PY())
    assert np.degrees(m.value[-1]) == approx(5, abs=0.1)
    
def test_roll_angle_ke_loop(keloop_tp: State):
    tp = keloop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = tp.superimpose_roll(np.radians(5))
    m = Measurement.roll_angle_proj(fl, tp, PZ())
    assert np.degrees(m.value[-1]) == approx(5, abs=0.1)
    
    
def test_roll_angle_45_loop(ke45loop_tp: State):
    tp = ke45loop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = tp.superimpose_roll(np.radians(-5))
    m = Measurement.roll_angle_proj(fl, tp, Point(0,1,1).unit())
    assert np.degrees(m.value[-1]) == approx(-5, abs=0.1)
    
    
def make_stallturn(duration: float=3, distance: Point=None, pos: Point=None, att: Quaternion=None):
    vel = distance / duration
    return State.from_transform(
        Transformation(pos, att),
        vel=vel
    ).extrapolate(duration).superimpose_rotation(PZ(), np.pi)


def test_roll_angle_proj():
    fl = Loop('loop', 30, np.pi/2, 50, r(0.5), 0).create_template(State.from_transform())
    tp = Loop('loop', 30, np.pi/2, 50, r(1.6), 0).create_template(State.from_transform(), fl.time)
    meas = Measurement.roll_angle_proj(fl, tp, PY())
    assert np.abs(np.round(meas.value[-1] / (2*np.pi)))==approx(1)


def test_pos_vis():
    assert Measurement._pos_vis(PY(1)) == approx(1)
    assert Measurement._pos_vis(Point(1, 1, 0)) == 1 / np.sqrt(2)
    assert Measurement._pos_vis(P0()) == 1


def test_depth_vis():
    assert Measurement.depth_vis(PY(170))[1] == 0.4
    assert Measurement.depth_vis(Point(170 * np.tan(np.radians(60)), 170, 0))[1] == 1.0


def test_roll_vis():

    def t_rvis(fla, tpa, yaw=0):
        tp = State.from_transform(Transformation(Point(0, 100, 0), Euldeg(fla, 0, yaw)), vel=PX(30))
        fl1 = State.from_transform(Transformation(Point(0, 100, 0), Euldeg(tpa, 0, yaw)), vel=PX(30))
        return Measurement._roll_vis(fl1, tp)[1][0]
    assert t_rvis(190, 170) == approx(1)
    assert t_rvis(170, 190) == approx(1)
    assert t_rvis(90, 90) == approx(0.1)
    assert t_rvis(90, 80) > 0.1

    assert t_rvis(190, 170, 90) == approx(1)
    assert t_rvis(170, 190, 90) == approx(1)
    assert t_rvis(90, 90, 90) == approx(1)
    assert t_rvis(90, 80, 90) == approx(1)


def test_get_axial_direction():

    def gpt(ke):    
        assert_almost_equal(
            Measurement.get_axial_direction(
                Loop('loop', 30, np.pi/2, 50, 0, ke).create_template(State.from_transform())
            ),
            Point(0, np.cos(ke), np.sin(ke))
        )  
    
    gpt(0)
    gpt(np.pi/4)
    gpt(-np.pi/4)
    gpt(np.pi/2)
    gpt(np.pi/8)
    gpt(-np.pi/8)
    gpt(np.pi*5/8)