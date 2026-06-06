from numbers import Number
import os
from json import load
import pandas as pd
from pathlib import Path
import numpy as np
from typing import Any
import re


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
        hasdeg = val.find("°")
        val = float(val.split("°")[0].strip())
        if hasdeg >= 0:
            val = np.radians(val)
        return val

    except Exception:
        return val if len(val) else None


def process_series(ser: pd.Series):
    if sum(ser == "True") + sum(ser == "False") == len(ser):
        return ser == "True"
    elif ser.dtype == object or ser.dtype == "string":

        try:
            vals = ser.str.extract(r'^([\d+]*\.?[\d]+)').iloc[:,0].astype(np.float64)
            if np.isnan(vals).any():
                return ser.values
            deglocs = ser.str.contains("°")
            if deglocs.any():
                pass
            return np.where(deglocs, np.radians(vals), vals)
            
        except Exception:
            return ser
    else:
        return ser.values


def parse_csv(file: Path | str | pd.DataFrame, **kwargs) -> pd.DataFrame:
    path = Path(file)
    df: pd.DataFrame = pd.read_csv(path, **({"comment": "#"} | kwargs), keep_default_na=False).apply(
        lambda x: x.str.strip() if x.dtype == object or x.dtype == "string" else x
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


def display_unit(value: Number, unit: str="", precision: int = 2) -> str:
    new_unit = re.sub(r"radians|radian|rad", "°", unit)
    if unit.find("rad") >= 0:
        val = f"{np.degrees(value):.{precision}f}"
    else:
        val = f"{value:.{precision}f}"
    return f"{val} {new_unit}"

def increment_name(base_name: str, existing_names: set[str]) -> str:
    if base_name not in existing_names:
        return base_name
    i = 1
    while f"{base_name}_{i}" in existing_names:
        i += 1
    return f"{base_name}_{i}"