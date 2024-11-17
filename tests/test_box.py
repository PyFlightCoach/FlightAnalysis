from flightanalysis.scoring.box import RectangularBox, TriangularBox

from pytest import approx
import geometry as g
import numpy as np
from flightdata import State


rbox = RectangularBox(1000, 1000, 1000, 1000, 0)
tbox =TriangularBox(np.radians(60), np.radians(60), 170, 150, 0)
def test_box_top_rectangular():
    assert rbox.top(g.PY(500))[1][0] == 1100

def test_box_top_triangular():
    assert tbox.top(g.PY(300))[1][0] == np.tan(np.radians(60)) * 300

def test_box_bottom_rectangular():
    assert rbox.bottom(g.PY(500))[1][0] == -100

def test_box_bottom_triangular():
    assert tbox.bottom(g.PY(300))[1][0] == approx(-np.tan(np.radians(15)) * 300)

def test_box_right_rectangular():
    assert rbox.right(g.PY(500))[1][0] == 500

def test_box_right_triangular():
    assert tbox.right(g.PY(300))[1][0] == np.tan(np.radians(60)) * 300   

def test_box_left_rectangular():
    assert rbox.right(g.PY(500))[1][0] == 500

def test_box_left_triangular():
    assert tbox.left(g.PY(300))[1][0] == approx(np.tan(np.radians(60)) * 300)

def test_box_back_rectangular():
    assert rbox.back(g.PY(300))[1][0] == 900

def test_box_back_triangular():
    assert tbox.back(g.PY(200))[1][0] == -25

def test_box_front_rectangular():
    assert rbox.front(g.PY(300))[1][0] == 100

def test_box_front_triangular():
    assert tbox.front(g.PY(0))[1][0] == -150


def test_leftbox_dg():
    
    direction, vs = rbox.left(g.PX(-450))
    
    rbox.bound_dgs.left.score(None, None, None)