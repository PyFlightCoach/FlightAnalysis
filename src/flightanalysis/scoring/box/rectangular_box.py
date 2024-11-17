import numpy as np
from dataclasses import dataclass
import geometry as g
from flightanalysis.scoring import DownGrades, DownGrade, Results
from schemas.maninfo import ManInfo
from flightdata import State
from .box import Box
from flightanalysis.scoring import Criteria, Results, Bounded, Single


@dataclass
class RectangularBox(Box):


    def _top(self, p: g.Point):
        return g.PZ(1), self.height + self.floor - p.z

    def _right(self, p: g.Point):
        return g.PX(1), self.width / 2 - p.x

    def _left(self, p: g.Point):
        return g.PX(-1), self.width / 2  + p.x

    def _bottom(self, p: g.Point):
        return g.PZ(-1), p.z - self.floor 


    def shift(self):
        pass