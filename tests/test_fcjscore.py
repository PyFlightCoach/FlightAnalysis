from json import load
from pytest import fixture, approx, mark
from flightdata import fcj
from flightanalysis.scripts.collect_scores import FCJScore
from flightanalysis.version import get_version
from flightanalysis import enable_logging
import pandas as pd
from pathlib import Path
from datetime import datetime


enable_logging()

@fixture
def fcjson() -> fcj.FCJ:
    return fcj.FCJ(**load(open('tests/data/scored_fcj.json', 'r')))


@fixture
def fcjr(fcjson) -> fcj.Result:
    return fcjson.fcs_scores[0]


def test_fcjr(fcjr: fcj.Result):
    assert fcjr.fa_version == '0.2.15.dev0+g7dd2339.d20240624'


@fixture() 
def fcjmr(fcjr)-> fcj.ManResult:
    return fcjr.manresults[1]


def test_fcjmr(fcjmr: fcj.ManResult):
    assert fcjmr.results[0].score.total == 8.004168387973385
    assert fcjmr.results[0].properties.difficulty == 1
    

def test_fcjmr_to_df(fcjmr: fcj.ManResult):
    df = fcjmr.to_df()
    assert df.loc[(3,False),'intra'] == 1.2343830594032101

    assert df.xs(False, level='truncate').shape[0] == 3


def test_fcjr_to_df(fcjr: fcj.Result, fcjmr: fcj.ManResult):
    df = fcjr.to_df()
    pd.testing.assert_frame_equal(df.loc[0], fcjmr.to_df())
    scores = df.loc[pd.IndexSlice[:,3,False]]
    #scores = df.xs((3, False), level=('difficulty', 'truncate'))
    assert scores.shape[0] == 17


def test_fcj_scoredf(fcjson: fcj.FCJ, fcjmr: fcj.ManResult):
    df = fcjson.score_df()
    pd.testing.assert_frame_equal(
        df.loc[('0.2.15.dev0+g7dd2339.d20240624',0)], 
        fcjmr.to_df()
    )


def test_man_df(fcjson: fcj.FCJ):
    df = fcjson.man_df()
    assert df.shape[0] == 17

def test_version_summary_df(fcjson: fcj.FCJ):
    df = fcjson.version_summary_df()
    assert df.kfac.total.iloc[0] == approx(455.6, rel=1)
    pass


def test_old_json():
    fcjson = fcj.FCJ.model_validate_json(open(Path('tests/data/old_json.json'), 'r').read())
    assert isinstance(fcjson, fcj.FCJ)

@fixture
def fcjscore(fcjson):
    return FCJScore.parse_fcj(Path('tests/data/scored_fcj.json'), fcjson)

def test_summary(fcjscore):
    summary = fcjscore.summary()
    assert summary['file'] == Path('tests/data/scored_fcj.json')
    assert summary['created'] == datetime(2024, 6, 21)
    assert summary['schedule'].name == 'p25'
    assert summary['0.2.15.dev0+g7dd2339.d20240624'] == approx(455.6, rel=1)
    assert summary['id'] == '00000154'

    

def test_fcjscore_run_analysis_done(fcjscore):
    fcjscorenew = fcjscore.run_analysis()
    assert get_version() in fcjscorenew.version_totals()


def test_fcjscore_parse_file():
    fcjscore = fcj.Score.model_validate_json(Path('tests/data/unscored_fcj.json').open().read())
    assert isinstance(fcjscore, fcj.Score)

@mark.skip("multiprocessing not working from pytest for some reason")
def test_fcjscore_run_analysis_not_done():
    fcjscore = fcj.Score.model_validate_json(Path('tests/data/unscored_fcj.json').open().read())
    fcjscore.scores = pd.DataFrame()
    fcjscorenew = fcjscore.run_analysis()
    assert get_version() in fcjscorenew.version_totals()
    pass