from __future__ import annotations

import inspect
from numbers import Number
import re
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
from flightdata.base import Collection


def tryval(val):
    try:
        if val[-1] == "°":
            return np.radians(float(val[:-1]))
        else:
            return float(val)
    except Exception:
        return val


@dataclass
class RefFunc:
    """A RefFunc is a reference to a function with some predefined keyword arguments.
    It serialises to a string that can be used to recreate the reference and
    argument presets by looking it up in an instance of RFuncBuilders.
    When the RefFunc is called it will call the referenced function with
    the argument presets. Additional arguments can be passed to the call.
    will error if arguments are duplicated.
    """

    name: str
    method: callable
    preset_kwargs: dict[str, Any] = field(default_factory=dict())
    description: str = ""

    def __getattr__(self, name):
        return getattr(self.method, name)

    def __call__(self, *args, meta=None, **kwargs):
        argspec = inspect.getfullargspec(self.method.measure if hasattr(self.method, 'measure') else self.method)
        if meta is not None and "meta" in argspec.args + argspec.kwonlyargs:
            kwargs=dict(**kwargs, meta=meta)
        return self.method(*args, **kwargs, **self.preset_kwargs)

    def __str__(self):
        return f"{self.name}({','.join([f'{k}:{str(v)}' for k, v in self.preset_kwargs.items()])})"

    @staticmethod
    def _getarg(arg: str) -> tuple[str, Any]:
        return arg.split(":")

    @staticmethod
    def from_str(
        funcs: dict[str, Callable], data: str, descriptions: dict[str, str] = {}
    ) -> RefFunc:
        try:
            if "(" not in data:
                return None
            name, sargs = data.split("(", 1)
            sargs = sargs.strip(") ,").split(",") if len(sargs) > 0 else []
            return RefFunc(
                name,
                funcs[name],
                {
                    k: tryval(v)
                    for k, v in dict([a.split(":") for a in sargs if len(a)]).items()
                },
                descriptions.get(name, ""),
            )
        except Exception as e:
            raise ValueError(f"Could not parse RefFunc from string: {data}") from e

    def describe(self) -> str:
        # Search for {} enclosing a valid python variable, optionally followed by : and a unit (any characters except })
        template_search = re.compile(r"\{([_a-zA-Z]+[_a-zA-Z0-9]*)+(:[^\}]*)?\}")
        description = self.description
        for match in template_search.finditer(self.description):
            template = match.group(0)
            variable = match.group(1)
            unit = match.group(2)[1:] if match.group(2) else None
            if variable in self.preset_kwargs:
                value = self.preset_kwargs[variable]
                if unit and unit.find("rad") >= 0:
                    value = np.degrees(value)
                    unit = re.sub(r"rad(ian)?(s)?", "°", unit)
                elif unit and unit.find("deg") >= 0:
                    unit = re.sub(r"deg(ree)?(s)?", "°", unit)
                if isinstance(value, Number):
                    value = f"{value:.2f}"
                description = description.replace(
                    template, f"{value}{unit if unit else ''}"
                )

        return description


class RefFuncs(Collection):
    VType = RefFunc
    uid = "name"

    def to_list(self):
        return [str(rf) for rf in self]


@dataclass
class RFuncBuilders:
    """A collection of functions to be referenced by a RefFunc."""

    funcs: dict[str, Callable]
    descriptions: dict[str, str] = field(default_factory=dict)

    def __getattr__(self, name):
        return lambda **kwargs: RefFunc(
            name, self.funcs[name], kwargs, self.descriptions.get(name, "")
        )

    def add(self, description: str = ""):
        def decorator(func: Callable):
            self.funcs[func.__name__] = func
            self.descriptions[func.__name__] = description
            return func

        return decorator

    def parse_csv_cell(self, data: str) -> list[RefFunc]:
        """parses things like: 'rf1(p1=1), rf2(p1=1, p2=2)'"""
        data = data.strip()
        rfuncs = []
        while "(" in data:
            name, data = data.split("(", 1)
            name = name.strip(" ,")
            sargs, data = data.split(")", 1)
            sargs = [s.split("=") for s in sargs.split(",")] if len(sargs) > 0 else []
            rfuncs.append(
                RefFunc(
                    name,
                    self.funcs[name],
                    {k.strip(): tryval(v.strip()) for k, v in dict(sargs).items()},
                    self.descriptions.get(name, ""),
                )
            )
        return rfuncs

    def parse(self, sfuncs: list[str] | str):
        if isinstance(sfuncs, str):
            return RefFunc.from_str(self.funcs, sfuncs, self.descriptions)
        elif np.ndim(sfuncs) > 0:
            return RefFuncs(
                [RefFunc.from_str(self.funcs, sf, self.descriptions) for sf in sfuncs]
            )
        else:
            return None
