from pytest import fixture, mark
from flightanalysis.scoring.criteria import Single, Exponential, Criteria, Combination, Continuous, Comparison, Bounded, ContinuousValue
from numpy.testing import assert_array_almost_equal
import numpy as np
from flightanalysis.scoring.criteria.inter.combination import parse_roll_string
from pytest import raises

@fixture
def single():
    return Single("test", Exponential(1,1))



def test_single_to_dict(single: Single):
    res = single.to_dict()
    
    assert res['kind'] == 'Single'
    crit = Criteria.from_dict(res)
    assert isinstance(crit, Single) 

def test_single_from_dict(single):
    res = Criteria.from_dict(single.to_dict())
    assert res == single


def test_single_call(single: Single):
    res = single(np.ones(4))
    assert_array_almost_equal(res[1], np.ones(4))
