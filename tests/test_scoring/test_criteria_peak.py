import numpy as np

from pytest import approx

from flightanalysis.scoring.criteria.exponential import Exponential
from flightanalysis.scoring.criteria.intra.peak import Peak, Trough
from flightanalysis.scoring.downgrade.downgrade import dg





def test_peak_identifies_the_biggest_distance_below_threshold():
    crit = Peak("test", Exponential(1,1), 1, -1)
    m = np.array([0.5, 0.8, 0.2, -1])

    signal = crit.prepare(m)
    errors, dgs, ids = crit(signal)

    assert len(dgs) == 1
    assert errors[0] == 2.0
    assert dgs[0] == 2.0
    assert ids[0] == 3
    

def test_trough_identifies_the_smallest_distance_below_threshold():
    crit = Trough("test", Exponential(1,1), 1, -1)
    m = np.array([0.5, 0.8, 0.2, -1])

    signal = crit.prepare(m)
    errors, dgs, ids = crit(signal)

    assert len(dgs) == 1
    assert errors[0] == approx(0.2)
    assert dgs[0] == approx(0.2)
    assert ids[0] == 1
    
