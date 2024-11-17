
from flightanalysis import ManParm, Collectors, Collector, Elements, Line, Exponential
from tests.f3a.criteria import F3A
from pytest import fixture, approx, mark
import numpy as np
 
@fixture
def mp():
    return ManParm(
        "length", 
        F3A.inter.length, 
        20.0,
        Collectors([
            Collector("e1", "length"),
            Collector("e2", "length")
        ])
    )

@fixture
def els(mp):
    return Elements([
        Line("e1", 30, 30, 0),
        Line("e2", 30, 10, 0)
    ])

def test_mp_value(mp):
    assert mp.value == 20

def test_mp_collect(mp, els):
    np.testing.assert_array_equal(list(mp.collect(els).values()), [30, 10]) 

@mark.skip
def test_mp_get_downgrades(mp: ManParm, els: Elements):
    res = mp.get_downgrades(els)
    np.testing.assert_array_almost_equal(res.dgs, [0,0.64201464])
    assert res.total == approx(0.64201464)


def test_serialization(mp):
    mpd = mp.to_dict()

    mp2 = ManParm.from_dict(mpd)
    assert isinstance(mp2.criteria.lookup, Exponential)