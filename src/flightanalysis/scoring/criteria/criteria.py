
from dataclasses import dataclass, field
from json import dumps
from typing import Literal
from uuid import uuid4

import numpy as np
import numpy.typing as npt

from flightanalysis.base.utils import all_subclasses

from .exponential import Exponential, free


@dataclass
class Criteria:
    name: str
    lookup: Exponential = field(default_factory=lambda: free)


    def prepare(self, value):
        return value

    def to_dict(self, include_name: bool = True):
        data = self.__dict__.copy()
        lookup = data.pop("lookup")
        if not include_name:
            data.pop("name", None)
        return dict(kind=self.__class__.__name__, lookup=lookup.__dict__, **data)

    def __repr__(self):
        return dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_dict(data: dict):
        if data is None:
            return None
        data = data.copy()
        kind = data.pop("kind")
        name = data.pop("name", str(uuid4()))
        for Crit in all_subclasses(Criteria):
            if Crit.__name__ == kind:
                lookup = data.pop("lookup")
                if "comparison" in data:
                    data.pop("comparison")
                return Crit(
                    name=name,
                    lookup=Exponential(**lookup),
                    **data,
                )
        raise ValueError(f"cannot parse Criteria from {data}")

    def to_py(self):
        _so = f"{self.__class__.__name__}(Exponential({self.name}{self.lookup.factor},{self.lookup.exponent}, {self.lookup.limit} )"
        if hasattr(self, "min_bound"):
            _so = f"{_so}, min_bound={self.min_bound}"
        if hasattr(self, "min_bound"):
            _so = f"{_so}, max_bound={self.max_bound}"
        if hasattr(self, "limit"):
            _so = f"{_so}, limit={self.limit}"
        return _so + ")"

    def describe(self, unit: str = "") -> str:
        return f"{self.__class__.__name__} Criteria"

    def short_description(self, unit: str = "") -> str:
        return self.__class__.__name__

    def local_error(
        self,
        sample: npt.NDArray,
        dt: npt.NDArray,
        direction: Literal["left", "right"],
    ):
        """The value of the error if the sample were to be cut at each point in time.
        if direction is right, the sample starts at the start and goes to the point.
        if right it starts at the point and goes to the end of the sample. 
        """
        raise NotImplementedError("local_error must be implemented in subclasses")

    def incremental_downgrade(
        self,
        local_dg: npt.NDArray,  # local_dg = self.lookup(local_error, limits),
        direction: Literal["left", "right"],
    ):
        """Calculate the total downgrade for the element if the sample ended at each point."""
        return local_dg


