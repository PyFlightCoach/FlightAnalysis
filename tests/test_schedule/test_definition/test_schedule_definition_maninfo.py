from flightanalysis.definition.maninfo import *
import numpy as np
from pytest import fixture
from geometry import PX

def minf(position, direction):
    return ManInfo("test", "t", 1, position, 
        BoxLocation(Height.BTM, direction, Orientation.UPRIGHT), 
        BoxLocation(Height.BTM))


def test_height():
    assert Height.BTM.calculate(170) == np.tan(np.radians(15)) * 170

def test_roll_angle():
    assert Orientation.UPRIGHT.roll_angle() == np.pi


def test_initial_position():
    assert np.sign(minf(Position.CENTRE, Direction.UPWIND).initial_position(170, -1).x[0]) == -1
    assert np.sign(minf(Position.CENTRE, Direction.DOWNWIND).initial_position(170, -1).x[0]) == 1
    assert minf(Position.END, Direction.DOWNWIND).initial_position(170, -1).x[0] == 0


def test_intitial_orientation():
    assert BoxLocation(Height.BTM,Direction.UPWIND, Orientation.UPRIGHT ).initial_rotation(1).transform_point(PX(1)).x[0] == -1
    assert BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT).initial_rotation(-1).transform_point(PX(1)).x[0] == 1


def test_box_location_serialize():
    bloc = BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT)
    dloc = bloc.to_dict()
    np.testing.assert_array_equal(list(dloc.values()), ["BTM", "UPWIND", "UPRIGHT"])

    bloc2 = BoxLocation.from_dict(dloc)
    assert bloc2.h == bloc.h
    assert bloc2.d == bloc.d
    assert bloc2.o == bloc.o


def test_minf_serialize():
    mi = minf(Position.CENTRE, Direction.UPWIND)
    md = mi.to_dict()
    assert md["name"] == mi.name
    assert md["position"] == mi.position.name

    mi2 = ManInfo.from_dict(md)
    assert mi2.name == mi.name

    