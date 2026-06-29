from pytest import approx, fixture
from flightanalysis.scoring.criteria import (
    AnyIntraCriteria,
    Deviation,
    Continuous,
    Bounded,
    Single,
    Exponential,
)
import numpy as np
import numpy.typing as npt
from typing import Literal


# sample index = [0, 1, 2, 3, 4, 5, 6, 7, 8, .., n-1 ]
# left cut     =                | <----- p = n-5 --->   = sample[p:]
# right cut    = <-----p = 5 -> |                       = sample[:p]


def compare_idg_to_call(
    crit: AnyIntraCriteria,
    sample: npt.NDArray,
    direction: Literal["left", "right"],
):  
    if direction == "right":
        _right_local_dg = [sum(crit(crit.prepare(sample[:i + 1]))[1]) for i in range(len(sample))]
    else:
        _right_local_dg = [sum(crit(crit.prepare(sample[i:]))[1]) for i in range(len(sample))]
    _right_ldg = crit.local_downgrade(crit.prepare(sample), None, direction)

    assert _right_ldg == approx(_right_local_dg)


def test_continouus_right_local_downgrade_matches__call__():
    crit = Continuous("t", Exponential(1, 1, None))
    # fmt: off
    #                    0, 1, 2, 3,  4,  5,  6, 7, 8, 9,10,11,12
    sample =   np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1]) 
    right_local_dg =    [0, 1, 2, 2,  3,  4,  4, 4, 5, 6, 7, 7, 7]
    # fmt: on
    _right_ldg = crit.local_downgrade(sample, None, "right")
    np.testing.assert_array_equal(_right_ldg, right_local_dg)
    compare_idg_to_call(crit, sample, "right")

def test_continouus_left_local_downgrade_matches__call__():
    crit = Continuous("t", Exponential(1, 1, None))
    # fmt: off
    #                   0, 1, 2, 3,  4,  5,  6, 7, 8, 9,10,11,12
    sample =  np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1])
    left_local_dg =    [7, 6, 5, 5,  4,  3,  3, 3, 2, 1, 0, 0, 0]
    # fmt: on
    _left_ldg = crit.local_downgrade(sample, None, "left")
    np.testing.assert_array_equal(_left_ldg, left_local_dg)
    compare_idg_to_call(crit, sample, "left")


def test_bounded_right_local_downgrade_matches__call__():
    crit = Bounded("t", Exponential(1, 1, None), 2, -2)
    sample =   np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1]) 
    compare_idg_to_call(crit, sample, "right")

def test_bounded_left_local_downgrade_matches__call__():
    crit = Bounded("t", Exponential(1, 1, None), 2, -2)
    sample =   np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1]) 
    compare_idg_to_call(crit, sample, "left")


def test_deviation_left_local_downgrade_matches__call__():
    crit = Deviation("t", Exponential(1, 1, None))
    sample =   np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1]) 
    compare_idg_to_call(crit, sample, "left")

def test_deviation_right_local_downgrade_matches__call__():
    crit = Deviation("t", Exponential(1, 1, None))
    sample =   np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1])  + 2
    compare_idg_to_call(crit, sample, "right")