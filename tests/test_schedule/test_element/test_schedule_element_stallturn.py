import numpy as np
from geometry import Point, Transformation
from pytest import mark

from flightanalysis.elements import StallTurn


@mark.skip
def test_create_template():
    template = StallTurn(30.0).create_template(Transformation())

    np.testing.assert_array_almost_equal(template[-1].pos.data[0], [0.0, 0.0, 0.0])

    np.testing.assert_array_almost_equal(
        Point.X(-1.0).data, template[-1].att.transform_point(Point.X(1.0)).data
    )
