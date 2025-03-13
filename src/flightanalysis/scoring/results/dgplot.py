
from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from flightdata import Collection
from flightdata.base import to_list
from flightanalysis.scoring.measurement import Measurement
from flightanalysis.scoring.criteria import Criteria
from dataclasses import dataclass
import geometry as g
from itertools import chain

def split_on_spaces(line, maxlen):
    outlines = []
    icount = 0
    while len(line[icount:]) > maxlen:
        nsplit = icount + line[icount : icount + maxlen].rfind(" ")
        outlines.append(line[icount:nsplit])
        icount = nsplit
    else:
        outlines.append(line[icount:].strip(" "))

    return outlines

@dataclass
class DGPlot:
    ename: str
    dgs: dict[str, float]
    location: g.Point

    def total(self):
        return sum(self.dgs.values())

    def total_str(self):
        return f"-{self.total():.2f}: {self.ename}"

    def summary(self, maxlen=30):
        lines = [split_on_spaces(f"-{v:.2f}: {k}", maxlen) for k, v in self.dgs.items()]
        return "<br>".join(list(chain(*lines)))
