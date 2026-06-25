
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
        direction: Literal["forward", "backward"] = "forward",
    ):
        """The value of the error if the sample were to be cut at each point in time.
        if direction is forward, the sample starts at the start and goes to the point.
        if backward it starts at the point and goes to the end of the sample. 
        """
        raise NotImplementedError("local_error must be implemented in subclasses")

    def incremental_downgrade(
        self,
        local_dg: npt.NDArray,  # local_dg = self.lookup(local_error, limits),
        direction: Literal["forward", "backward"] = "forward",
    ):
        """Calculate the total downgrade for the element if the sample ended at each point."""

        # the downgrade delta of each point
        if direction == "forward":
            dg_increment = np.diff(local_dg, prepend=local_dg[0])
        else:
            dg_increment = np.diff(local_dg[::-1], prepend=local_dg[-1])[::-1]

        # downgrade deltas cant be negative ( if it is negative its because of a different clump)
        dg_increment = np.where(dg_increment > 0, dg_increment, 0)

        return (
            dg_increment.cumsum()
            if direction == "forward"
            else dg_increment[::-1].cumsum()[::-1]
        )


    def calculate_increments(
        self, sample: npt.NDArray, direction: Literal["forward", "backward"]
    ):
        le = self.local_error(sample, direction)
        ldg = self.lookup(le)
        return self.incremental_downgrade(ldg, direction)

    def process_increments(
        self,
        local_error: npt.NDArray,
        local_dg: npt.NDArray,
        direction: Literal["forward", "backward"] = "forward",
    ):
        """This takes the incremental outputs and returns something that looks like __call__"""
        clumps = np.split(local_error, np.argwhere(local_error == 0).T[0])
        clump_lengths = np.array([len(clump) for clump in clumps])
        clump_locs = np.cumsum(clump_lengths) - 1  # the index of each clump
        dgids = np.array(
            [clump_locs[i] for i, b in enumerate([len(c) > 1 for c in clumps]) if b]
        )  # the end of the non-zero clumps

        return local_error[dgids], local_dg[dgids], dgids