from flightanalysis import ScheduleAnalysis, ManDef
from flightanalysis.analysis.analysis_json import AnalysisJson
from flightanalysis.analysis.manoeuvre_analysis.schema import MA
from pytest import fixture


@fixture
def ajson_basic():
    return AnalysisJson.model_validate_json(open('tests/data/analysis_json_basic.json', 'r').read())


@fixture
def ajson_full():
    return AnalysisJson.model_validate_json(open('tests/data/analysis_json_full.json', 'r').read())


def test_ajson_basic(ajson_basic: AnalysisJson):
    assert ajson_basic.sourceBin is None
    assert isinstance(ajson_basic.mans[0], MA)

def test_ajson_full(ajson_full: AnalysisJson):
    assert ajson_full.mans[0].mdef['info']['short_name'] == 'sLoop'
    assert ajson_full.tStart == ajson_full.flown[0].time    

    #ajson_full.mans[0].flown['data'][0]['t']

#def test_sa_parse_ajson_basic(ajson_basic: AnalysisJson):
#    sa = ScheduleAnalysis.parse_dict(ajson_basic)
#    assert isinstance(sa, ScheduleAnalysis)
#
#def test_sa_parse_ajson_full(ajson_full: AnalysisJson):
#    sa = ScheduleAnalysis.parse_ajson(ajson_full)
#    assert isinstance(sa, ScheduleAnalysis)
#    assert len(sa) == 17
#    assert isinstance(sa[0].mdef, ManDef)
    