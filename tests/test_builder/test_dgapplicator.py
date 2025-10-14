import numpy as np
import geometry as g
from flightanalysis.builders.dgapplicator import ElTag, checktagstring, tag_elements, checktag
from pytest import fixture
from flightdata import State
from flightanalysis import (
    Manoeuvre,
    Elements,
    Line,
    Loop,
    Snap,
    Spin,
    StallTurn,
    TailSlide,
)


@fixture
def manoeuvre():
    return Manoeuvre(
        Elements(
            [
                Line("entry_line", 30, 50, 0),
                Loop("loop1", 30, np.pi / 2, 40, 0, 0),
                Line("pad1", 30, 30, 0),
                Line("roll1", 30, 50, np.pi),
                Line("pad2", 30, 30, 0),
                Loop("loop2", 30, np.pi / 2, 40, 0, 0),
            ]
        ),
        Line("exit_line", 30, 50, 0),
    )


@fixture
def tps(manoeuvre: Manoeuvre):
    return manoeuvre.create_template(g.Transformation(), npoints="min")


def test_tag_elements(manoeuvre: Manoeuvre, tps: dict[str, State]):
    tags = tag_elements(manoeuvre.all_elements(), tps)
    # fmt: off
    assert tags == dict(
        entry_line= set([ElTag.LINE, ElTag.ENTRYLINE , ElTag.HORIZONTAL ]),
        loop1= set([ElTag.LOOP, ElTag.HORIZONTALENTRY, ElTag.VERTICALEXIT ]),
        pad1= set([ElTag.LINE, ElTag.VERTICAL ]),
        roll1= set([ElTag.LINE, ElTag.VERTICAL, ElTag.ROLL ]),
        pad2= set([ElTag.LINE, ElTag.VERTICAL ]),
        loop2= set([ElTag.LOOP, ElTag.VERTICALENTRY, ElTag.HORIZONTALEXIT ]),
        exit_line= set([ElTag.LINE, ElTag.EXITLINE, ElTag.HORIZONTAL ]),
    )
    # fmt: on


def test_checktag():
    #empty has and hasnot
    assert checktag(
        tag=set([ElTag.LINE, ElTag.ENTRYLINE, ElTag.HORIZONTAL]),
    )

    # confirm it has
    assert checktag(
        tag=set([ElTag.LINE, ElTag.ENTRYLINE, ElTag.HORIZONTAL]),
        has=set([ElTag.LINE, ElTag.HORIZONTAL]),
    )

    # missing a has
    assert not checktag(
        tag=set([ElTag.LINE, ElTag.ENTRYLINE, ElTag.HORIZONTAL]),
        has=set([ElTag.LOOP, ElTag.HORIZONTAL]),
    )

    # it has but shouldnt 
    assert not checktag(
        tag=set([ElTag.LINE, ElTag.ENTRYLINE, ElTag.HORIZONTAL]),
        hasnot=set([ElTag.ENTRYLINE]),
    )

    # confirm it hasnot
    assert checktag(
        tag=set([ElTag.LINE, ElTag.HORIZONTAL]),
        hasnot=set([ElTag.ENTRYLINE]),
    )

def test_checktagstring():
    assert not checktagstring(
        set([ElTag.LINE, ElTag.ENTRYLINE, ElTag.HORIZONTAL]),
        "LINE, HORIZONTAL, !ENTRYLINE"
    )