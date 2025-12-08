from flightanalysis.scoring.criteria.exponential import Exponential
import numpy as np
from pytest import approx


def test_to_from_simple():
    expo = Exponential.simple(1, np.pi, 6, False)
    assert expo.to_simple() == approx((1, np.pi, 6))
    expo = Exponential.simple(1.5, np.pi, 6, False)
    assert expo.to_simple() == approx((1.5, np.pi, 6))
    