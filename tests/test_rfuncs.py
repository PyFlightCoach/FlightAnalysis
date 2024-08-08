from flightanalysis.base.ref_funcs import RFuncBuilders
from pytest import fixture


@fixture
def builders():

    builders = RFuncBuilders({})
    
    @builders.add
    def func1(a: int, b: int):
        return a + b

    @builders.add
    def func2(a: int, b: int):
        return a - b

    return builders


def test_decorator(builders):
    f =  builders.func1(b=2)
    assert f(1) == 3
    assert builders.func2(b=2)(2) == 0