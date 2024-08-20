from json import load
from pytest import fixture, approx, mark
from flightanalysis.fcjson import FCJResult, FCJManResult, FCJ
from flightanalysis.scripts.collect_scores import FCJScore
from flightanalysis.version import get_version
from flightanalysis import enable_logging
import pandas as pd
from pathlib import Path
from datetime import datetime


enable_logging()

@fixture
def fcj() -> FCJ:
    return FCJ(**load(open('tests/data/scored_fcj.json', 'r')))


@fixture
def fcjr(fcj) -> FCJResult:
    return fcj.fcs_scores[0]


def test_fcjr(fcjr: FCJResult):
    assert fcjr.fa_version == '0.2.15.dev0+g7dd2339.d20240624'


@fixture() 
def fcjmr(fcjr)-> FCJManResult:
    return fcjr.manresults[1]


def test_fcjmr(fcjmr: FCJManResult):
    assert fcjmr.results[0].score.total == 8.004168387973385
    assert fcjmr.results[0].properties.difficulty == 1
    

def test_fcjmr_to_df(fcjmr: FCJManResult):
    df = fcjmr.to_df()
    assert df.loc[(3,False),'intra'] == 1.2343830594032101

    assert df.xs(False, level='truncate').shape[0] == 3


def test_fcjr_to_df(fcjr: FCJResult, fcjmr: FCJManResult):
    df = fcjr.to_df()
    pd.testing.assert_frame_equal(df.loc[0], fcjmr.to_df())
    scores = df.loc[pd.IndexSlice[:,3,False]]
    #scores = df.xs((3, False), level=('difficulty', 'truncate'))
    assert scores.shape[0] == 17


def test_fcj_scoredf(fcj: FCJ, fcjmr: FCJManResult):
    df = fcj.score_df()
    pd.testing.assert_frame_equal(
        df.loc[('0.2.15.dev0+g7dd2339.d20240624',0)], 
        fcjmr.to_df()
    )


def test_man_df(fcj: FCJ):
    df = fcj.man_df()
    assert df.shape[0] == 17

def test_version_summary_df(fcj: FCJ):
    df = fcj.version_summary_df()
    assert df.kfac.total.iloc[0] == approx(455.6, rel=1)
    pass


def test_old_json():
    fcj = FCJ.model_validate_json(open(Path('tests/data/old_json.json'), 'r').read())
    assert isinstance(fcj, FCJ)

@fixture
def fcjscore(fcj):
    return FCJScore.parse_fcj(Path('tests/data/scored_fcj.json'), fcj)

def test_summary(fcjscore):
    summary = fcjscore.summary()
    assert summary['file'] == Path('tests/data/scored_fcj.json')
    assert summary['created'] == datetime(2024, 6, 21)
    assert summary['schedule'].name == 'p25'
    assert summary['0.2.15.dev0+g7dd2339.d20240624'] == approx(455.6, rel=1)
    assert summary['id'] == '00000154'

    

def test_fcjscore_run_analysis_done(fcj, fcjscore):
    fcjscorenew = fcjscore.run_analysis()
    assert get_version() in fcjscorenew.version_totals()


def test_fcjscore_parse_file():
    fcjscore = FCJScore.parse_file(Path('tests/data/unscored_fcj.json'))
    assert isinstance(fcjscore, FCJScore)

@mark.skip("multiprocessing not working from pytest for some reason")
def test_fcjscore_run_analysis_not_done():
    fcjscore = FCJScore.parse_file('tests/data/unscored_fcj.json')
    fcjscore.scores = pd.DataFrame()
    fcjscorenew = fcjscore.run_analysis()
    assert get_version() in fcjscorenew.version_totals()
    pass