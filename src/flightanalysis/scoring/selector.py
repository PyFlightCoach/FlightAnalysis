from dataclasses import dataclass
from typing import Callable
from flightdata import State


type SelectorFunc = Callable[[State], list[int]]


@dataclass
class Selector:
    name: str
    selector: SelectorFunc
    left: bool
    right:bool

    def __call__(self, fl: State, **kwargs) -> list[int]:
        return self.selector(fl, **kwargs)

    @property
    def __name__(self):
        return self.name