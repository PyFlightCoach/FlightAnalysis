from flightanalysis.elements.split_optimiser import discrete_golden
import numpy as np






def test_discrete_golden():
    assert discrete_golden(lambda steps: int(steps)**2, -10, 10) == 0
    assert discrete_golden(lambda steps: int(steps)**2, 5, 10) == 5


if __name__ == "__main__":
    test_discrete_golden()