from flightanalysis.data import get_json_resource



def test_load_json_resurce():
    p23def = get_json_resource("f3a_p23_schedule.json")

    assert p23def['tHat']['info']['name'] == "Top Hat"