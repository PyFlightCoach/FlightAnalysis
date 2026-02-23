from pytest import fixture

from flightanalysis import ManParm, ManParms, ComboSetting, ComboSettings, Combination


@fixture
def mps():
    return ManParms(
        [
            ManParm("mp1", Combination("mp1", desired=[[0], [1]]), defaul=0),
            ManParm("mp2", Combination("mp2", desired=[[0], [1]]), defaul=0),
        ]
    )

def test_all_permutations_produced(mps: ManParms):
    permutations: list[ComboSettings] = mps.permutations()

    assert len(permutations) == 4



@fixture
def cs():
    return ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)])


def test_combosettings_check_behaviour(cs: ComboSettings):
    assert cs.check(ComboSettings([ComboSetting("mp1", 0)]))
    assert cs.check(ComboSettings([ComboSetting("mp2", 1)]))
    assert cs.check(ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)]))
    assert not cs.check(ComboSettings([ComboSetting("mp1", 1)]))
    assert not cs.check(ComboSettings([ComboSetting("mp2", 0)]))
    assert cs.check(None)
    assert cs.check(ComboSettings([]))
    assert cs.check(ComboSettings([ComboSetting("mp3", 0)]))


def test_clean_combosettings_keeps_incomplete_entries(mps: ManParms):
    

    cleaned = mps.clean_combosettings([
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 0)]),
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)]),
        ComboSettings([ComboSetting("mp1", 1), ComboSetting("mp2", 0)]),
    ])
    assert len(cleaned) == 3

def test_clean_combosettings_removes_redundant_entries(mps: ManParms):

    cleaned = mps.clean_combosettings([
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 0)]),
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)]),
        ComboSettings([ComboSetting("mp1", 1), ComboSetting("mp2", 0)]),
        ComboSettings([ComboSetting("mp1", 1), ComboSetting("mp2", 1)]),
    ]
    )
    assert len(cleaned) == 0
