from random import sample

from pytest import fixture
from flightanalysis.scoring.criteria import (
    AnyIntraCriteria,
    Limit,
    Continuous,
    Single,
    Exponential,
)
import numpy as np
import numpy.typing as npt
from typing import Literal


def compare_idg_at_point(
    crit: AnyIntraCriteria,
    sample: npt.NDArray,
    point: int,
    direction: Literal["left", "right"],
):
    
    mistakes, dgs, dgids = crit(sample[:point+1] if direction == "right" else sample[point:])
    errors = crit.local_error(sample, None, direction)
    idgs = crit.incremental_downgrade(crit.lookup(errors), direction)

    assert idgs[point] == sum(dgs)



def test_continouus_local_error_matches__call__():
    crit = Continuous("t", Exponential(1, 1, None))
    
    sample = np.array([0, 1, 2, 1, -1, -2, -1, 0, 1, 2, 3,2,1])

    compare_idg_at_point(crit, sample, 5, "left")
    
    compare_idg_at_point(crit, sample, 5, "right")
    compare_idg_at_point(crit, sample, 3, "right")
    compare_idg_at_point(crit, sample, len(sample)-1, "right")
    compare_idg_at_point(crit, sample, len(sample)-1, "left")
    compare_idg_at_point(crit, sample, 0, "left")
    
    


