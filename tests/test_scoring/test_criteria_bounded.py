from pytest import fixture, mark
from flightanalysis.scoring.criteria import Single, Exponential, Criteria, Combination, Continuous, Comparison, Bounded, ContinuousValue
from numpy.testing import assert_array_almost_equal
import numpy as np
from flightanalysis.scoring.criteria.inter.combination import parse_roll_string
from pytest import raises




@fixture
def maxbound():
    return Bounded("test", Exponential(1,1),  max_bound=0)

def test_maxbound_prepare(maxbound: Bounded):
    testarr = np.concatenate([np.ones(3), np.zeros(3), np.ones(3), np.zeros(3)])
    sample = maxbound.prepare(testarr)
    np.testing.assert_array_equal(sample, testarr)


def test_bounded_call(maxbound: Bounded):
    testarr = np.concatenate([np.ones(3), np.zeros(3), np.ones(3), np.zeros(3)])
    res = maxbound(testarr)
    
    np.testing.assert_array_equal(res[2], [3, 9])
    np.testing.assert_array_equal(res[0], [0.25, 0.25])
    np.testing.assert_array_equal(res[1], [0.25, 0.25])

def test_maxbound_serialise(maxbound: Bounded):
    data = maxbound.to_dict()
    mb2 = Criteria.from_dict(data)
    assert isinstance(mb2, Bounded)
    assert mb2.max_bound==0
    

@fixture
def inside():
    return Bounded(Exponential(1,1), min_bound=-1, max_bound=1)

def test_inside_allin(inside: Bounded):
    sample = inside.prepare(np.zeros(11))
    np.testing.assert_array_equal(sample, np.zeros(11))
    
def test_inside_above(inside: Bounded):
    sample = inside.prepare(np.full(11, 2))
    np.testing.assert_array_equal(sample, np.ones(11))
    
def test_inside_below(inside: Bounded):
    sample = inside.prepare(np.full(11, -2))
    np.testing.assert_array_equal(sample, np.ones(11))



@fixture
def outside():
    return Bounded(Exponential(1,1), min_bound=1, max_bound=-1)

def test_outside_allin(outside: Bounded):
    sample = outside.prepare(np.zeros(11))
    np.testing.assert_array_equal(sample, np.ones(11))
    
def test_outside_above(outside: Bounded):
    sample = outside.prepare(np.full(11, 2))
    np.testing.assert_array_equal(sample, np.zeros(11))
    
def test_outside_below(outside: Bounded):
    sample = outside.prepare(np.full(11, -2))
    np.testing.assert_array_equal(sample, np.zeros(11))
    

def test_outside_prepare(outside: Bounded):
    
    np.testing.assert_array_equal(outside.prepare(np.full(11, 0.5)), np.full(11, 0.5))    
    np.testing.assert_array_equal(outside.prepare(np.full(11, -0.5)), np.full(11, 0.5))    



@fixture
def ndbound():
    return Bounded(Exponential(20,1), -np.radians(15), np.radians(15))


