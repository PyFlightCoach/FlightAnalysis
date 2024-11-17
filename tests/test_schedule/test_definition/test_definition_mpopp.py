from pytest import fixture

from flightanalysis import ManParms, Opp, ManParm
from tests.example.builder import f3amb

@fixture
def mps():
    return f3amb.mps


def test_number_opp(mps):
    assert (mps.loop_radius + 10)(mps) == mps.loop_radius.value + 10
    assert (10 + mps.loop_radius)(mps) == mps.loop_radius.value + 10

def test_mp_opp_mp(mps):
    mpopp = mps.loop_radius + mps.line_length

    assert isinstance(mpopp, Opp)
    
    assert mpopp(mps) == mps.loop_radius.value + mps.line_length.value
    assert str(mpopp) == "(loop_radius+line_length)"

def test_mp_opp_mp_div(mps):
    mpopp = mps.loop_radius / mps.line_length
    assert isinstance(mpopp, Opp)
    assert str(mpopp) == "(loop_radius/line_length)"
    assert mpopp(mps) == mps.loop_radius.value / mps.line_length.value


def test_mp_opp_mpopp(mps):
    mpopp = mps.loop_radius + (mps.line_length * mps.loop_radius)

    assert str(mpopp) == "(loop_radius+(line_length*loop_radius))"
    assert mpopp(mps) == mps.loop_radius.value + (mps.loop_radius.value * mps.line_length.value)


def test_mp_opp_float(mps):
    mpopp = mps.loop_radius * 2

    assert str(mpopp) == "(loop_radius*2)"

    assert mpopp(mps) == mps.loop_radius.value * 2


def test_mpfun_mp(mps):
    mpfun = abs(mps.loop_radius)

    assert str(mpfun) == "abs(loop_radius)"
    assert mpfun(mps) == abs(mps.loop_radius.value)


def test_parse_mpfun(mps):
    mpopp = abs(mps.loop_radius)
    mpopp2 = ManParm.parse(str(mpopp), mps)
    assert str(mpopp2) == str(mpopp)
    assert mpopp2(mps) == abs(mps.loop_radius.value)


def test_parse_mpopp(mps):
    mpopp = mps.loop_radius + mps.line_length
    mpopp2 = ManParm.parse(str(mpopp), mps)
    assert str(mpopp2) == str(mpopp)
    assert mpopp2(mps) == mps.loop_radius.value + mps.line_length.value

def test_parse_combo(mps):
    mpo = (mps.loop_radius * mps.line_length) - abs(mps.speed + (mps.line_length - mps.line_length))
    assert str(mpo) == "((loop_radius*line_length)-abs((speed+(line_length-line_length))))"
    mpo2 = ManParm.parse(str(mpo), mps)

    assert str(mpo) == str(mpo2)
    assert mpo2(mps) == mpo(mps)


def test_mpopp_sum(mps):
    mpo = 170 - sum([mps.line_length + mps.loop_radius for _ in range(3)])
    assert mpo(mps) == -385