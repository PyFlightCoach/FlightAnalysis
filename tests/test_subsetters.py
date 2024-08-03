from flightanalysis.scoring.f3a_subsetters import subs
import numpy as np



def test_from_funcs():
    assert len(subs.available) == 9


def test_all():
    assert np.all(
        subs.available['all'](np.ones(5)) == np.arange(5)
    )


def test_getattr():
    assert np.all(
        subs.all()(np.zeros(5)) == np.arange(5)
    )


def test_from_string():
    assert np.all(
        subs.from_str('all()')(np.zeros(5)) == np.arange(5)
    )

    