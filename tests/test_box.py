from flightanalysis.builders.IAC.box import unlimited_box
from flightanalysis.builders.f3a.box import box
from pytest import approx
import geometry as g
import numpy as np
from flightdata import State

def test_box_top_rectangular():
    assert unlimited_box.top(g.PY(500))[1][0] == 1100

def test_box_top_triangular():
    assert box.top(g.PY(300))[1][0] == np.tan(np.radians(60)) * 300

def test_box_bottom_rectangular():
    assert unlimited_box.bottom(g.PY(500))[1][0] == -100

def test_box_bottom_triangular():
    assert box.bottom(g.PY(300))[1][0] == approx(-np.tan(np.radians(15)) * 300)

def test_box_right_rectangular():
    assert unlimited_box.right(g.PY(500))[1][0] == 500

def test_box_right_triangular():
    assert box.right(g.PY(300))[1][0] == np.tan(np.radians(60)) * 300   

def test_box_left_rectangular():
    assert unlimited_box.right(g.PY(500))[1][0] == 500

def test_box_left_triangular():
    assert box.left(g.PY(300))[1][0] == approx(np.tan(np.radians(60)) * 300)

def test_box_back_rectangular():
    assert unlimited_box.back(g.PY(300))[1][0] == 900

def test_box_back_triangular():
    assert box.back(g.PY(200))[1][0] == -25

def test_box_front_rectangular():
    assert unlimited_box.front(g.PY(300))[1][0] == 100

def test_box_front_triangular():
    assert box.front(g.PY(0))[1][0] == -150


def test_leftbox_dg():
    
    direction, vs = unlimited_box.left(g.PX(-450))
    
    unlimited_box.bound_dgs.left.score(None, None, None)