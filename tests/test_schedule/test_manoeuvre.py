from flightanalysis import Manoeuvre, Loop, Line
from pytest import fixture
import numpy as np
import geometry as g
from flightdata import State


@fixture
def man():
    return Manoeuvre([
        Line("entry_line", 30, 20, 0),
        Loop("loop1", 30, np.pi, 50.0, 0, 0),
        Line("hline", 30, 50, 0),
        Loop("loop2", 30, np.pi, 50.0, 0, 0)
    ], Line("exit_line", 30, 20, 0), "man1")

@fixture
def tp(man: Manoeuvre):
    itrans = g.Transformation(g.Euldeg(180, 0,0))
    return man.create_template(itrans)

def test_create_template(tp: State):
    
    assert tp[0].pos == g.Point(0, 0, 0)
    assert tp[0].vel == g.PX(30)
    assert len(tp.labels.element) == 5
    tp.plot().show()
    tp.plotlabels('element').show()

def test_create_template_with_al(man: Manoeuvre, tp: State):
    el0: Line = man.elements[0]
    tpel = el0.create_template(tp[0], tp.element[0])

    assert len(tpel) == len(tp.element[0])
    np.testing.assert_array_equal(tpel.t, tp.element[0].t)

    tp2 = man.create_template(tp[0].transform, tp)

    assert len(tp2) == len(tp)


