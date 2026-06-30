from pytest import approx, fixture
from flightanalysis.scoring.criteria import (
    AnyIntraCriteria,
    Deviation,
    Total,
    Continuous,
    Bounded,
    Peak,
    Trough,
    Single,
    Limit,
    Threshold,
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
    slices = [slice(None, i+1) if direction == "right" else slice(i, None) for i in range(len(sample))]
    _local_dg = [
            sum(crit(crit.prepare(sample[s]), dt=np.ones(len(sample[s])))[1])
            for s in slices
        ]

    _right_ldg = crit.local_downgrade(crit.prepare(sample), dt=np.ones(len(sample)), direction=direction)

    np.testing.assert_array_almost_equal(_right_ldg, _local_dg)


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
    sample = np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1])
    compare_idg_to_call(crit, sample, "right")


def test_bounded_left_local_downgrade_matches__call__():
    crit = Bounded("t", Exponential(1, 1, None), 2, -2)
    sample = np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3, 2, 1])
    compare_idg_to_call(crit, sample, "left")


def test_deviation_left_local_downgrade_matches__call__():
    crit = Deviation("t", Exponential(1, 1, None))
    sample = np.array([0, 1, 2, 1, 0])
    compare_idg_to_call(crit, sample, "left")


def test_deviation_right_local_downgrade_matches__call__():
    crit = Deviation("t", Exponential(1, 1, None))
    sample = np.array([0, 1, 2, 1, 0]) + 2
    compare_idg_to_call(crit, sample, "right")


def test_total_left_local_downgrade_matches__call__():
    crit = Total("t", Exponential(1, 1, None))
    sample = np.array([0, 1, 2, 1, 0]) 
    compare_idg_to_call(crit, sample, "left")


def test_total_right_local_downgrade_matches__call__():
    crit = Total("t", Exponential(1, 1, None))
    sample = np.array([0, 1, 2, 1, 0]) 
    compare_idg_to_call(crit, sample, "right")

def test_peak_left_local_downgrade_matches__call__():
    crit = Peak("t", Exponential(1, 1, None), 1)
    sample = np.array([0, 1, 2, 2, 3])
    compare_idg_to_call(crit, sample, "left")


def test_peak_right_local_downgrade_matches__call__():
    crit = Peak("t", Exponential(1, 1, None), 1)
    sample = np.array([0, 1, 2, 2, 3])
    compare_idg_to_call(crit, sample, "right")

def test_trough_left_local_downgrade_matches__call__():
    crit = Trough("t", Exponential(1, 1, None), 1)
    sample = np.array([0, 1, 2, 2, 3])
    compare_idg_to_call(crit, sample, "left")


def test_trough_right_local_downgrade_matches__call__():
    crit = Trough("t", Exponential(1, 1, None), 1)
    sample = np.array([0, 1, 2, 2, 3])
    compare_idg_to_call(crit, sample, "right")

def test_single_left_local_downgrade_matches__call__():
    crit = Single("t", Exponential(1, 1, None))
    sample = np.array([0, 1, 2, 2, 3])
    compare_idg_to_call(crit, sample, "left")

def test_limit_left_local_downgrade_matches__call__():
    crit = Limit("t", Exponential(1, 1, None), 1)
    sample = np.array([0, 1, 2, 2, 3])
    compare_idg_to_call(crit, sample, "left")