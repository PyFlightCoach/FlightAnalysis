from flightanalysis.scoring.box import RectangularBox, TriangularBox, Box
import geometry as g
import numpy as np

rbox = RectangularBox(1000, 1000, 1000, 1000, 0, {})
tbox =TriangularBox(np.radians(60), np.radians(60), 170, 150, 0, {})
def test_box_top_rectangular():
    assert rbox.top(g.PY(500))[1][0] == 1000

def test_box_top_triangular():
    assert tbox.top(g.PY(300))[1][0] == np.tan(np.radians(60)) * 300

def test_box_bottom_rectangular():
    assert rbox.bottom(g.PY(500))[1][0] == 0

def test_box_bottom_triangular():
    assert tbox.bottom(g.PY(300))[1][0] == 0

def test_box_right_rectangular():
    assert rbox.right(g.PY(500))[1][0] == 500


def test_box_tofrom_dict():
    tbox = TriangularBox(np.radians(60), np.radians(60), 170, 150, 0, {})
    sbox = tbox.to_dict()
    tbox2 = Box.from_dict(sbox)
    assert tbox.depth == tbox2.depth

