import numpy as np
from dataclasses import dataclass
import geometry as g
from flightanalysis.scoring import DownGrades, DownGrade, Results
from flightanalysis.definition.maninfo import ManInfo
from flightdata import State
from .box import Box
from flightanalysis.scoring import Criteria, Results, Bounded, Single


@dataclass
class RectangularBox(Box):


    def top(self, p: g.Point):
        return g.PZ(1), p.z - self.height - self.floor

    def right(self, p: g.Point):
        return g.PX(1), p.x - self.width / 2

    def left(self, p: g.Point):
        return g.PX(-1), - self.width / 2 - p.x

    def bottom(self, p: g.Point):
        return g.PZ(-1), self.floor - p.z


