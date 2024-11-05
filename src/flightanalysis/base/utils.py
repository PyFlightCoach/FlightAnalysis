import os
from json import load


def combine_args(names: list[str], *args, **kwargs) -> dict:
    """Combine the args and kwargs into a dict with the names as keys"""
    _kwargs = {}
    for i, n in enumerate(names):
        if i < len(args):
            _kwargs[n] = args[i]
        if n in kwargs:
            _kwargs[n] = kwargs[n]
    return _kwargs


def validate_json(file: dict|str|os.PathLike) -> dict:
    if isinstance(file, dict):
        return file
    elif isinstance(file, str) or isinstance(file, os.PathLike):
        with open(file, 'r') as f:
            return load(f)
    else:
        raise ValueError("expected a dict, str or os.PathLike")
    
