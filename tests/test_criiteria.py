from pytest import fixture, mark
from flightanalysis.scoring.criteria import Single, Exponential, Criteria, Combination, ContRat, ContAbs, Comparison, MaxBound, InsideBound, OutsideBound, Continuous
from flightanalysis.scoring import Measurement
from numpy.testing import assert_array_almost_equal
import numpy as np
import geometry as g

@fixture
def single():
    return Single(Exponential(1,1))


@fixture
def contrat():
    return ContRat(Exponential(1,1))

@fixture
def contabs():
    return ContAbs(Exponential(1,1))


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

@mark.skip('this now just pics the last value')
def test_single_call(single: Single):
    res = single('test', Measurement(np.ones(4), 0, g.PX(4), np.ones(4)))
    assert_array_almost_equal(res.dgs, np.ones(4))

def test_continuous_from_str(contrat):
    res = Criteria.from_dict(contrat.to_dict())
    assert res == contrat

@mark.skip('This is more complicated as the smoothing needs to be considered')
def test_continuous_call_ratio(contrat):
    [2,3,4,5,6,7], 
    res = contrat(
        'test', 
        Measurement(np.array([1.1, 1.2, 1, 1.2, 1.3, 1.1]), 1, g.PX(6), np.ones(6))
    )
    assert_array_almost_equal(res.keys, [3,6])
    assert_array_almost_equal(res.dgs, [0.1,0.3])

def test_continuous_call_absolute(contabs):
    res = contabs(
        'test',
        Measurement(np.array([0.1, 0.2, 0, -0.1, -0.2, -0.1]), 0, g.PX(6), np.ones(6))
    )
    assert_array_almost_equal(res.keys, [1,4])
    assert_array_almost_equal(res.dgs, [0.1,0.2])


def test_combination_from_dict(combination):
    res = Criteria.from_dict(combination.to_dict())
    assert res == combination


def test_comparison_call(comparison):
    ids, error, res = comparison(['a', 'b', 'c', 'd'], [1,1.3,1.2,1])
    assert_array_almost_equal(res, [0, 0.3, 1.3/1.2-1, 0.2])


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
    return MaxBound(Exponential(1,1),  0)

def test_maxbound(maxbound: MaxBound):
    testarr = np.concatenate([np.ones(3), np.zeros(3), np.ones(3), np.zeros(3)])
    sample = maxbound.prepare(testarr, 0)
    np.testing.assert_array_equal(sample, testarr)


def test_bounded_call(maxbound: MaxBound):
    testarr = np.concatenate([np.ones(3), np.zeros(3), np.ones(3), np.zeros(3)])
    res = maxbound(
        'test',
        Measurement(testarr, 0, g.PX(12), np.ones(12)) 
    )
    
    np.testing.assert_array_equal(res.keys, [1, 7])
    np.testing.assert_array_equal(res.errors, [1, 1])
    np.testing.assert_array_equal(res.dgs, [0.25, 0.25])

def test_maxbound_serialise(maxbound: MaxBound):
    data = maxbound.to_dict()
    mb2 = Criteria.from_dict(data)
    assert isinstance(mb2, MaxBound)
    assert mb2.bound==0
    
    
    
@fixture
def inside():
    return InsideBound(Exponential(1,1), [-1, 1])

def test_inside_allin(inside: InsideBound):
    sample = inside.prepare(np.zeros(11), 0)
    np.testing.assert_array_equal(sample, np.zeros(11))
    
def test_inside_above(inside: InsideBound):
    sample = inside.prepare(np.full(11, 2), 0)
    np.testing.assert_array_equal(sample, np.ones(11))
    
def test_inside_below(inside: InsideBound):
    sample = inside.prepare(np.full(11, -2), 0)
    np.testing.assert_array_equal(sample, np.ones(11))
    

@fixture
def outside():
    return OutsideBound(Exponential(1,1), [-1, 1])


def test_outside_allin(outside: OutsideBound):
    sample = outside.prepare(np.zeros(11), 0)
    np.testing.assert_array_equal(sample, np.ones(11))
    
def test_outside_above(outside: InsideBound):
    sample = outside.prepare(np.full(11, 2), 0)
    np.testing.assert_array_equal(sample, np.zeros(11))
    
def test_outside_below(outside: OutsideBound):
    sample = outside.prepare(np.full(11, -2), 0)
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

def test_contabs_mistakes():
    data = np.array([0,1,2,1,0,1,2,1,0,1,2,1,0])
    np.testing.assert_array_equal(
        ContAbs.mistakes(*mistakes_inputs(data)), 
        [2,2,2]
    )

    data = np.array([2,1,0,1,2,1,0,1,2,1,0,1,2])
    np.testing.assert_array_equal(
        ContAbs.mistakes(*mistakes_inputs(data)), 
        [2,2,2]
    )

def test_contrat_mistakes():
    data = np.array([0,1,2,1,0,1,2,1,0,1,2,1,0]) + 2
    np.testing.assert_array_equal(
        ContRat.mistakes(*mistakes_inputs(data)), 
        [1,1,1,1,1,1]
    )

    data = 4 - np.array([0,1,2,1,0,1,2,1,0,1,2,1,0])
    np.testing.assert_array_equal(
        ContRat.mistakes(*mistakes_inputs(data)), 
        [1,1,1,1,1,1]
    )
