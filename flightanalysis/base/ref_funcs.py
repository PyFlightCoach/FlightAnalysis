from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any
from flightdata.base import Collection


@dataclass
class RefFunc:
    """A RefFunc is a reference to a function with some predefined keyword arguments.
    It serialises to a string that can be used to recreate the reference and
    argument presets by looking it up in an RFuncBuilders object.
    When the RefFunc is called it will call the referenced function with
    the argument presets. Additional arguments can be passed to the call.
    will error if arguments are duplicated
    """

    name: str
    method: callable
    preset_kwargs: dict[str, Any] = field(default_factory=dict())

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs, **self.preset_kwargs)

    def __str__(self):
        return f'{self.name}({",".join([f"{k}:{str(v)}" for k,v in self.preset_kwargs.items()])})'

    @staticmethod
    def _getarg(arg: str) -> tuple[str, Any]:
        return arg.split(":")

    @staticmethod
    def from_str(funcs: dict[str, Callable], data: str) -> RefFunc:
        name = data.split("(")[0]
        sargs = data.split("(")[1][:-1]
        sargs = sargs.split(",") if len(sargs) > 0 else []
        return RefFunc(
            name,
            funcs[name],
            dict([a.split(":") for a in sargs]),
        )


@dataclass
class RFuncBuilders:
    """A collection of functions to be referenced by a RefFunc."""
    funcs: dict[str, Callable]

    def __getattr__(self, name):
        return lambda **kwargs : RefFunc(name, self.funcs[name], kwargs)

    def add(self, func):
        self.funcs[func.__name__] = func
        return func


class RefFuncs(Collection):
    VType = RefFunc
    uid = "name"

    def to_list(self):
        return [str(rf) for rf in self]
    
    @staticmethod
    def parse(builders: RFuncBuilders, funcs: list[str]):
        return RefFuncs([RefFunc.from_str(builders.funcs, f) for f in funcs])