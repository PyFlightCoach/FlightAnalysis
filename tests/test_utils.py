from pathlib import Path
from pytest import fixture
from flightanalysis.base.utils import parse_csv, tryval
import numpy as np

@fixture
def csv():
    return Path("tests/data/fcs_csv.csv")

def test_parse_csv(csv):
    df = parse_csv(csv, sep=",")
    assert list(df.columns) == ["a", "b", "c", "d"]
    assert df.iloc[0].to_dict() == {"a": 1, "b": "test1", "c": True, "d": 4}
    assert df.iloc[1].to_dict() == {"a": 2, "b": "test3", "c": False, "d": np.radians(20)}
    assert df.iloc[2].to_dict() == {"a": 3, "b": "test3", "c": False, "d": np.radians(20)}


def test_tryval():
    assert tryval("123") == 123
    assert tryval("45.67") == 45.67
    assert tryval("test") == "test"
    assert tryval("0") == 0
    assert tryval("180°") == np.pi