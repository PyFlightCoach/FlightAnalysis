from pytest import fixture
from flightanalysis.scoring.criteria import Single, Exponential, Criteria, Combination, Continuous, Comparison, Bounded, ContinuousValue
from flightanalysis.scoring import Measurement
from numpy.testing import assert_array_almost_equal
import numpy as np
import geometry as g

@fixture
def single():
    return Single(Exponential(1,1))


@fixture
def continuous():
    return Continuous(Exponential(1,1))

@fixture
def contvalue():
    return ContinuousValue(Exponential(1,1))


@fixture
def combination():
    return Combination(desired=[[1,-1],[-1,1]])


@fixture
def comparison():
    return Comparison(Exponential(1,1))


def test_single_to_dict(single: Single):
    res = single.to_dict()
    
    assert res['kind'] == 'Single'

def test_single_from_dict(single):
    res = Criteria.from_dict(single.to_dict())
    assert res == single


def test_single_call(single: Single):
    res = single(np.ones(4))
    assert_array_almost_equal(res[1], np.ones(4))

def test_continuous_from_str(continuous):
    res = Criteria.from_dict(continuous.to_dict())
    assert res == continuous


def test_continuous_call_ratio(continuous):
    #[2,3,4,5,6,7], 
    res = continuous(np.array([1.1, 1.2, 1, 1.2, 1.3, 1.1]))
    assert_array_almost_equal(res[0], [0.1,0.3])
    assert_array_almost_equal(res[1], [0.1,0.3])
    assert_array_almost_equal(res[2], [1,4])

def test_continuous_call_absolute(contvalue):
    res = contvalue(np.array([1.1, 1.2, 1, 1.2, 1.3, 1.1]))
    assert_array_almost_equal(res[2], [1,2,4, 5])
    assert_array_almost_equal(res[1], [0.1,0.2, 0.3, 0.2])


def test_combination_from_dict(combination):
    res = Criteria.from_dict(combination.to_dict())
    assert res == combination


def test_comparison_call(comparison):
    errors, dgs, ids = comparison([1,1.3,1.2,1])
    assert_array_almost_equal(dgs, [0, 0.3, 1.3/1.2-1, 0.2])


def test_combination_append_roll_sum():
    combo = Combination.rollcombo('4X4')
    combo = combo.append_roll_sum()
    assert combo.desired.shape==(2,8)

    np.testing.assert_array_equal(
        combo.desired / (2*np.pi),
        np.array(
            [[0.25,0.25,0.25,0.25,0.25,0.5,0.75,1],
            [-0.25,-0.25,-0.25,-0.25,-0.25,-0.5,-0.75,-1]]
        )
    )
    
    
@fixture
def maxbound():
    return Bounded(Exponential(1,1),  max_bound=0)

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
    

def test_get_peak_locs():
    res = Continuous.get_peak_locs(np.array([0,1,2,1,0,1,2,1,0,1,2]))
    np.testing.assert_array_equal(np.linspace(0,10,11).astype(int)[res], [2,6,10])

    res = Continuous.get_peak_locs(np.array([0,1,2,1,0,1,2,1,0,1,2]), True)
    np.testing.assert_array_equal(np.linspace(0,10,11).astype(int)[res], [0,4,8])

    res = Continuous.get_peak_locs(np.array([2,1,0,1,2,1,0,1,2,1,0]))
    np.testing.assert_array_equal(np.linspace(0,10,11).astype(int)[res], [0,4,8])

    res = Continuous.get_peak_locs(np.array([2,1,0,1,2,1,0,1,2,1,0]), True)
    np.testing.assert_array_equal(np.linspace(0,10,11).astype(int)[res], [2,6,10])


def mistakes_inputs(data):
    return data, Continuous.get_peak_locs(data), Continuous.get_peak_locs(data, True)

def test_continuous_mistakes():
    data = np.array([0,1,2,1,0,1,2,1,0,1,2,1,0])
    np.testing.assert_array_equal(
        Continuous.mistakes(*mistakes_inputs(data)), 
        [2,2,2]
    )

    data = np.array([2,1,0,1,2,1,0,1,2,1,0,1,2])
    np.testing.assert_array_equal(
        Continuous.mistakes(*mistakes_inputs(data)), 
        [2,2,2]
    )

def test_continuousvalue_mistakes():
    data = np.array([0,1,2,1,0,1,2,1,0,1,2,1,0]) + 2
    np.testing.assert_array_equal(
        ContinuousValue.mistakes(*mistakes_inputs(data)), 
        [2,-2,2,-2,2,-2]
    )

    data = 4 - np.array([0,1,2,1,0,1,2,1,0,1,2,1,0])
    np.testing.assert_array_equal(
        ContinuousValue.mistakes(*mistakes_inputs(data)), 
        [-2, 2,-2, 2,-2, 2]
    )


@fixture
def ndbound():
    return Bounded(Exponential(20,1), -np.radians(15), np.radians(15))
