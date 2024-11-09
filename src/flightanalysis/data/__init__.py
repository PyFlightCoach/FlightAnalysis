from importlib.resources import files
from json import load


def get_json_resource(name):
    return load(files("flightanalysis.data").joinpath(name).open('r'))

def get_file(name):
    return files("flightanalysis.data").joinpath(name)

def list_resources(rtype: str):
    return [file.name for file in files("flightanalysis.data").iterdir() if file.name.endswith(f"{rtype}.json")]

if __name__ == "__main__":
    resources = list_resources('schedule')
    print(resources)
    data = get_json_resource(resources[0])
