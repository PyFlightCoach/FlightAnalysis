from pytest import fixture
import numpy as np
from flightanalysis import ElDef, Loop, ManParms
from flightanalysis.definition.builders.manbuilder import f3amb 
from flightanalysis.definition.builders.f3a_downgrades import DGGrps

@fixture
def mps():
    return f3amb.mps


@fixture
def loopdef(mps):
    return ElDef.build(
        Loop,
        "test", 
        [mps.speed, np.pi/2, mps.loop_radius, 0, False],
        DGGrps.loop
)
    

def test_call(loopdef: ElDef, mps: ManParms):
    loop = loopdef(mps)

    assert loop.radius == mps.loop_radius.defaul


