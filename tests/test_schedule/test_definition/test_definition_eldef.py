from pytest import fixture
import numpy as np
from flightanalysis import ElDef, Loop, ManParms
from flightanalysis.builders.f3a.manbuilder import f3amb 
from flightanalysis.builders.f3a.downgrades import dg_applicator

@fixture
def mps():
    return f3amb.mps


@fixture
def loopdef(mps):
    return ElDef.build(
        Loop,
        "test", 
        [mps.speed, np.pi/2, mps.loop_radius, 0, False],
)
    

def test_call(loopdef: ElDef, mps: ManParms):
    loop = loopdef(mps)

    assert loop.radius == mps.loop_radius.defaul


