from pytest import fixture
from schemas import Position, BoxLocation, ManInfo, Height, Direction, Orientation
from flightanalysis import Manoeuvre,  ManDef
from tests.example.builder.manbuilder import f3amb

import numpy as np
from json import load



@fixture(scope="session")
def vline() -> ManDef:
    return f3amb.create(ManInfo("Vertical Line", "vline", 2,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),
        [
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2),    
        ]
    )

    

@fixture(scope="session")
def man(vline: ManDef):
    return vline.create(vline.info.initial_transform(170,1))

def test_create(man: Manoeuvre):
    assert isinstance(man, Manoeuvre)
    
def test_collect(vline: ManDef, man: Manoeuvre):
    downgrades = vline.mps.collect(man)
    assert np.all(downgrades.speed.downgrades==0)
 

def test_to_from_dict(vline: ManDef):
       
    vld = vline.to_dict()

    vl2 = ManDef.from_dict(vld)#


    assert isinstance(vld, dict)
    assert isinstance(vl2, ManDef)
    

    man = vl2.create(vl2.info.initial_transform(170,1))
    downgrades = vl2.mps.collect(man)

    assert np.all(downgrades.speed.downgrades==0)


@fixture
def p23_def_dict():
    with open("flightanalysis/data/p23.json", "r") as f:
        return load(f)


def test_mdef_parse_dict(p23_def_dict):
    iSp = ManDef.from_dict(p23_def_dict["trgle"])
    pass


