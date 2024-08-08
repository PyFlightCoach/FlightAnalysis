from flightanalysis.scoring.selectors import f3a_sels
import numpy as np



def test_from_funcs():
    assert len(f3a_sels.available) == 9


def test_all():
    assert np.all(
        f3a_sels.available['all'](np.ones(5)) == np.arange(5)
    )


def test_getattr():
    assert np.all(
        f3a_sels.all()(np.zeros(5)) == np.arange(5)
    )


def test_from_string():
    assert np.all(
        f3a_sels.from_str('all()')(np.zeros(5)) == np.arange(5)
    )

    