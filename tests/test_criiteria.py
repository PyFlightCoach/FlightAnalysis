from pytest import fixture
from flightanalysis.scoring.criteria import Criteria, Single, Exponential, Continuous, Combination, Comparison
from numpy.testing import assert_array_almost_equal
import numpy as np


@fixture
def single():
    return Single(Exponential(1,1), 'absolute')


@fixture
def continuous():
    return Continuous(Exponential(1,1), 'ratio')

@fixture
def combination():
    return Combination(desired=[[1,-1],[-1,1]])


@fixture
def comparison():
    return Comparison(Exponential(1,1), 'ratio')


def test_single_to_dict(single: Single):
    res = single.to_dict()
    
    assert res['kind'] == 'Single'

def test_single_from_dict(single):
    res = Criteria.from_dict(single.to_dict())
    assert res == single

def test_single_call(single: Single):
    ids, dgs = single([0,1,2,3], [1,2,3,4])
    assert_array_almost_equal(dgs, [1,2,3,4])
    assert_array_almost_equal(ids, [0,1,2,3])


def test_continuous_from_str(continuous):
    res = Criteria.from_dict(continuous.to_dict())
    assert res == continuous

def test_continuous_call_ratio(continuous):
    ids, dgs = continuous([2,3,4,5,6,7], [1.1, 1.2, 1, 1.2, 1.3, 1.1])
    assert_array_almost_equal(ids, [3,6])
    assert_array_almost_equal(dgs, [0.1,0.3])

def test_continuous_call_absolute(continuous):
    ids, dgs = continuous([2,3,4,5,6,7], [0.1, 0.2, 0, -0.1, -0.2, -0.1])
    assert_array_almost_equal(ids, [3,6])
    assert_array_almost_equal(dgs, [0.1,0.2])


def test_combination_from_dict(combination):
    res = Criteria.from_dict(combination.to_dict())
    assert res == combination


def test_comparison_call(comparison):
    ids, res = comparison(['a', 'b', 'c', 'd'], [1,1.3,1.2,1])
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