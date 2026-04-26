from pytest import fixture, mark
from flightanalysis.scoring.criteria import Single, Exponential, Criteria, Combination, Continuous, Comparison, Bounded, ContinuousValue
from numpy.testing import assert_array_almost_equal
import numpy as np
from flightanalysis.scoring.criteria.inter.combination import parse_roll_string
from pytest import raises


@fixture
def combination():
    return Combination("test", desired=[[1,-1],[-1,1]])


@fixture
def comparison():
    return Comparison("test", Exponential(1,1))



@mark.skip
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


def test_parse_roll_string():
    assert parse_roll_string("2X4") == [0.25, 0.25]
    assert parse_roll_string("1/2") == [0.5]
    assert parse_roll_string("2x2") == [0.5, 0.5]
    assert parse_roll_string("1") == [1]
    assert parse_roll_string("1.5") == [1.5]


    with raises(ValueError):
        parse_roll_string("sdv")