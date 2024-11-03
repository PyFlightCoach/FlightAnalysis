
import numpy as np
from dataclasses import dataclass
import geometry as g
from .box import Box



@dataclass
class TriangularBox(Box):

    def _top_angle(self, p: g.Point):
        return g.PZ(1), np.arctan2(p.z, p.y) - self.height

    def _top(self, p: g.Point):
        return g.PZ(1), p.y * np.tan(self.height) - p.z

    def _right_angle(self, p: g.Point):
        return g.PX(1), np.arctan2(p.x, p.y) - self.width / 2

    def _right(self, p: g.Point):
        return g.PX(1), p.y * np.tan(self.width / 2) - p.x

    def _left_angle(self, p: g.Point):
        return g.PX(-1), -self.width / 2 - np.arctan2(p.x, p.y)

    def _left(self, p: g.Point):
        return g.PX(-1), p.y * np.tan(self.width / 2) + p.x

    def _bottom(self, p: g.Point):
        return g.PZ(-1), p.z - p.y * np.tan(self.floor)

    def centre_angle(self, p: g.Point):
        return g.PX(1), np.arctan2(p.x, p.y)

    def trace_front(self):
        import plotly.graph_objects as go
        fd = self.front(g.P0())
        return go.Mesh3d(
            x=[fd, fd, fd, fd], 
            y=[0, 0, 0, 0], 
            z=[0, 0, 0, 0], 
            i=[0, 1, 2, 3], 
            j=[1, 2, 3, 0], 
            k=[2, 3, 0, 1],
            opacity=0.4
        )

    def trace_box(self):
        import plotly.graph_objects as go

        xlim=170*np.tan(np.radians(60))
        ylim=170
        return [go.Mesh3d(
            #  0  1     2     3      4    5      6
            x=[0, xlim, 0,    -xlim, xlim, 0,   -xlim], 
            y=[0, ylim, ylim,  ylim, ylim, ylim, ylim], 
            z=[0, 0,    0,     0,    xlim, xlim, xlim], 
            i=[0, 0, 0, 0, 0], 
            j=[1, 2, 1, 3, 4], 
            k=[2, 3, 4, 6, 6],
            opacity=0.4
        )]
