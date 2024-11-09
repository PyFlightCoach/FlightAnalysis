from importlib.metadata import version


def get_version():
    return version("flightanalysis")


__version__ = get_version()
