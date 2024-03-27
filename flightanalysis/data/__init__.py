from pkg_resources import resource_stream, resource_listdir
from json import loads


all_resources = resource_listdir("flightanalysis", "data")

def get_json_resource(name):
    data = resource_stream(__name__, f"{name.lower()}.json").read().decode()
    return loads(data)


def list_resources(rtype: str):
    return [fname for fname in all_resources if fname.endswith(f'_{rtype}.json')]

