from pytest import fixture

from flightanalysis import ManParm, ManParms, ComboSetting, ComboSettings, Combination, ComboSet


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



def test_clean_comboset(mps: ManParms):

    # given a ManParms containing mp1 and mp2, each with two options and a comboset with all combinations 
    # of mp1, none of mp2 and all combinations of OPTION. 
    cset = ComboSet(
        [
            ComboSetting("mp1", 0),
            ComboSetting("mp1", 1),
            ComboSetting("OPTION", 0),
            ComboSetting("OPTION", 1),
        ]
    )

    # when the comboset is cleaned, with noptions set to 2
    cleaned = mps.clean_comboset(cset, noptions=2)
    
    # then there should be no entries left
    assert len(cleaned) == 0

    # when the comboset is cleaned, with noptions set to 3
    cleaned = mps.clean_comboset(cset, noptions=3)

    # then the OPTION entries should be left
    assert len(cleaned) == 2
    assert ComboSetting("OPTION", 0) in cleaned.values()
    assert ComboSetting("OPTION", 1) in cleaned.values()
    assert ComboSetting("OPTION", 2) not in cleaned.values()


def test_combosettings_check_behaviour():
    # given a ComboSettings with mp1=0 and mp2=1
    cs = ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)])
    
    # then it should check true for any ComboSettings that are a subset of it, 
    assert cs.check(ComboSettings([ComboSetting("mp1", 0)]))
    assert cs.check(ComboSettings([ComboSetting("mp2", 1)]))
    assert cs.check(ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)]))
    
    # false for any ComboSettings that contain a different value for mp1 or mp2, 
    assert not cs.check(ComboSettings([ComboSetting("mp1", 1)]))
    assert not cs.check(ComboSettings([ComboSetting("mp2", 0)]))

    # and true for any ComboSettings that does not include mp1 or mp2. 
    # It should also check true for None and an empty ComboSettings.
    assert cs.check(None)
    assert cs.check(ComboSettings([]))
    assert cs.check(ComboSettings([ComboSetting("mp3", 0)]))


def test_clean_combosettings_keeps_incomplete_entries(mps: ManParms):
    

    cleaned = mps.clean_combosettings([
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 0)]),
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)]),
    ])
    assert len(cleaned) == 1
    assert cleaned[0] == ComboSettings([ComboSetting("mp1", 0)])



def test_clean_combosettings_removes_redundant_entries(mps: ManParms):

    cleaned = mps.clean_combosettings([
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 0)]),
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)]),
        ComboSettings([ComboSetting("mp1", 1), ComboSetting("mp2", 0)]),
        ComboSettings([ComboSetting("mp1", 1), ComboSetting("mp2", 1)]),
    ]
    )
    assert len(cleaned) == 0

def test_clean_combosettings_removes_redundant_leaves_incomplete(mps: ManParms):
    cleaned = mps.clean_combosettings([
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 0)]),
        ComboSettings([ComboSetting("mp1", 0), ComboSetting("mp2", 1)]),
        ComboSettings([ComboSetting("mp1", 1)])
    ]
    )
    assert len(cleaned) == 0

