from pytest import fixture, mark
from flightanalysis.scoring.criteria import Single, Exponential, Criteria, Combination, Continuous, Comparison, Bounded, ContinuousValue
from numpy.testing import assert_array_almost_equal
import numpy as np
from flightanalysis.scoring.criteria.inter.combination import parse_roll_string
from pytest import raises


@fixture
def continuous():
    return Continuous("test", Exponential(1,1))

@fixture
def contvalue():
    return ContinuousValue("test", Exponential(1,1))



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
