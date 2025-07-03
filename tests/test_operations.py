import numpy as np
from pytest import fixture

import flightanalysis.definition.operations as o
from flightanalysis.definition.manparm import ManParm, ManParms
from flightanalysis.definition.operations.sumopp import SumOpp
from flightanalysis.scoring.criteria import Comparison
from flightanalysis.scoring.criteria.inter.combination import Combination
from flightanalysis.definition.operations.operation import bracksplit


@fixture
def coll():
    return ManParms(
        [
            ManParm("a", Comparison("test"), 1),
            ManParm("b", Comparison("test"), 1),
            ManParm("c", Comparison("test"), 1),
            ManParm("d", Combination("test", desired=np.array([[1, 2, 3], [4, 5, 6]])), 0),
            ManParm("e", Combination("test", desired=np.array([[1], [2]])), 0),
        ]
    )



def test_parse_operator(coll):
    opp = o.Opp.parse("(a+b)", coll)
    assert isinstance(opp, o.MathOpp)
    assert opp(coll) == 2


def test_itemopp(coll):
    opp = o.Opp.parse(coll.d[1], coll)
    assert isinstance(opp, o.ItemOpp)
    assert opp(coll) == 2
    coll.d.defaul = 1
    assert opp(coll) == 5

def test_itemopp_single(coll):
    opp = o.Opp.parse("e[0]", coll)
    assert isinstance(opp, o.ItemOpp)
    assert opp(coll) == 1
    coll.e.defaul = 1
    assert opp(coll) == 2


def test_parse_sum(coll):
    opp = o.Opp.parse("sum([a,b,c])", coll)
    assert isinstance(opp, o.SumOpp)


def test_parse_nested_function(coll):
    opp = o.Opp.parse("sum([c,max(a,b)])", coll)
    assert isinstance(opp, o.SumOpp)

    opp = o.Opp.parse("max(c,sum([a,b,c]))", coll)
    assert isinstance(opp, o.FunOpp)
    assert isinstance(opp.a, ManParm)
    assert isinstance(opp.b, SumOpp)


def test_bracksplit():
    assert bracksplit("a,b,c") == ["a", "b", "c"]
    assert bracksplit("(a,b),c") == ["(a,b)", "c"]
    assert bracksplit("max(a,b),sum([2,d,min(g,h)]),f[d]") == [
        "max(a,b)",
        "sum([2,d,min(g,h)])",
        "f[d]",
    ]
