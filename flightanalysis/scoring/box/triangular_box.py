
import numpy as np
from dataclasses import dataclass
import geometry as g
from .box import Box



@dataclass
class TriangularBox(Box):

    def top_angle(self, p: g.Point):
        return g.PZ(1), np.arctan2(p.z, p.y) - self.height

    def top(self, p: g.Point):
        return g.PZ(1), p.y * np.tan(self.height) - p.z

    def right_angle(self, p: g.Point):
        return g.PX(1), np.arctan2(p.x, p.y) - self.width / 2

    def right(self, p: g.Point):
        return g.PX(1), p.y * np.tan(self.width / 2) - p.x

    def left_angle(self, p: g.Point):
        return g.PX(-1), -self.width / 2 - np.arctan2(p.x, p.y)

    def left(self, p: g.Point):
        return g.PX(-1), p.y * np.tan(self.width / 2) - p.x

    def bottom(self, p: g.Point):
        return g.PZ(-1), p.z - p.y * np.tan(self.floor)

    def centre_angle(self, p: g.Point):
        return g.PX(1), np.arctan2(p.x, p.y)
