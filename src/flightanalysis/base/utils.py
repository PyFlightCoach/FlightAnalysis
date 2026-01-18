from numbers import Number
import os
from json import load
import pandas as pd
from pathlib import Path
import numpy as np
from typing import Any


def combine_args(names: list[str], *args, **kwargs) -> dict:
    """Combine the args and kwargs into a dict with the names as keys"""
    _kwargs = {}
    for i, n in enumerate(names):
        if i < len(args):
            _kwargs[n] = args[i]
        if n in kwargs:
            _kwargs[n] = kwargs[n]
    return _kwargs


def validate_json(file: dict | str | os.PathLike) -> dict:
    if isinstance(file, dict):
        return file
    elif isinstance(file, str) or isinstance(file, os.PathLike):
        with open(file, "r") as f:
            return load(f)
    else:
        raise ValueError("expected a dict, str or os.PathLike")


def df_insert(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Insert a column into a dataframe at a specific location"""
    if df.empty:
        return None
    return pd.concat(
        [
            pd.DataFrame({k: [v] * len(df) for k, v in kwargs.items()}),
            df.reset_index(drop=True),
        ],
        axis=1,
    )


def tryval(val):
    try:
        if val[-1] == "°":
            return np.radians(float(val[:-1]))
        else:
            return float(val)
    except Exception:
        return val if len(val) else None


def process_series(ser: pd.Series):
    if sum(ser == "True") + sum(ser == "False") == len(ser):
        return ser == "True"
    elif ser.dtype == object:
        try:
            deglocs = ser.str.endswith("°")
            if sum(deglocs):
                vals = ser.str.rstrip("°").astype(float)
                return np.where(deglocs, np.radians(vals), vals)
            else:
                return ser.astype(float)
        except Exception:
            return ser
    else:
        return ser


def parse_csv(file: Path | str | pd.DataFrame, **kwargs) -> pd.DataFrame:
    path = Path(file)
    df: pd.DataFrame = pd.read_csv(path, **({"comment": "#"} | kwargs), keep_default_na=False).apply(
        lambda x: x.str.strip() if x.dtype == object else x
    )
    df.columns = [c.strip() for c in df.columns]
    return df.apply(process_series)


def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def replace_parameters(data: dict | list | str | Number, parameters: dict):
    if isinstance(data, dict):
        return {k: replace_parameters(v, parameters) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_parameters(v, parameters) for v in data]
    elif isinstance(data, str) and data.startswith("parameters."):
        return parameters[data.split(".")[1]]
    else:
        return data


def replace_any_depth_value(d: Any, old_value: Any, new_value: Any) -> dict:
    if isinstance(d, dict):
        return {
            k: replace_any_depth_value(v, old_value, new_value) for k, v in d.items()
        }
    elif isinstance(d, list):
        return [replace_any_depth_value(v, old_value, new_value) for v in d]
    elif d.__class__ is old_value.__class__ and d == old_value:
        return new_value
    else:
        return d
