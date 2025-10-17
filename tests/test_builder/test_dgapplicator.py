import numpy as np
import geometry as g
from flightanalysis.builders.dgapplicator import ElTag, checktagstring, tag_elements, checktag, parse_tagstring
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
        entry_line= set([ElTag.LINE , ElTag.HORIZONTAL ]),
        loop1= set([ElTag.LOOP, ElTag.HORIZONTALENTRY, ElTag.VERTICALEXIT ]),
        pad1= set([ElTag.LINE, ElTag.VERTICAL ]),
        roll1= set([ElTag.LINE, ElTag.VERTICAL, ElTag.ROLL ]),
        pad2= set([ElTag.LINE, ElTag.VERTICAL ]),
        loop2= set([ElTag.LOOP, ElTag.VERTICALENTRY, ElTag.HORIZONTALEXIT ]),
        exit_line= set([ElTag.LINE,ElTag.HORIZONTAL ]),
    )
    # fmt: on


def test_parse_tagstring():
    check = parse_tagstring("LINE, HORIZONTAL, !ROLL")
    
    #exact match
    assert check(set([ElTag.LINE, ElTag.HORIZONTAL])) 
    
    #got something it shouldnt have
    assert not check(set([ElTag.LINE, ElTag.HORIZONTAL, ElTag.ROLL]))
    
    #got some things that dont matter
    assert check(set([ElTag.LINE, ElTag.HORIZONTAL, ElTag.HORIZONTALENTRY, ElTag.HORIZONTALEXIT]))

    #missing something it should have
    assert not check(set([ElTag.LINE, ElTag.VERTICAL]))
    
