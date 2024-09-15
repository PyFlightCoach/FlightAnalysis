import numpy as np
from dataclasses import dataclass
import geometry as g
from flightanalysis.scoring import DownGrades


@dataclass
class Box:
    dgs: DownGrades
    width: float
    height: float
    depth: float
    distance: float
    floor: float = np.radians(15)

    def top(self, p: g.Point):
        raise NotImplementedError
    
    def right(self, p: g.Point):
        raise NotImplementedError
    
    def left(self, p: g.Point):
        raise NotImplementedError
    
    def bottom(self, p: g.Point):
        raise NotImplementedError

    def inside(self, p: g.Point):
        return p.y - self.distance

    def outside(self, p: g.Point):
        return self.distance + self.depth - p.y

    def to_dict(self, longdgs=False):
        return dict(
            Kind=self.__class__.__name__,
            dgs=self.dgs.to_dict() if longdgs else self.dgs.to_list(),
            width=self.width,
            height=self.height,
            depth=self.depth,
            distance=self.distance,
            floor=self.floor,
        )
    
    @classmethod
    def from_dict(Cls, data: dict, dgs: DownGrades):
        return {C.__name__: C for C in Cls.__subclasses__()}[data.pop("Kind")](
            dgs.subset(data['dgs']),
            data["width"],
            data["height"],
            data["depth"],
            data["distance"],
            data["floor"],
        )


@dataclass
class TriangularBox(Box):
    dgs: DownGrades
    width = np.radians(120)
    height = np.radians(60)
    depth =25
    distance = 150
    floor = np.radians(15)

    def top(self, p: g.Point):
        return p.y * np.tan(self.height) - p.z
        
    def right(self, p: g.Point):
        return p.y * np.tan(self.width / 2) - p.x

    def left(self, p: g.Point):
        return p.x - p.y * np.tan(self.width / 2)

    def bottom(self, p: g.Point):
        return p.z - p.y * np.tan(self.floor)


@dataclass
class RectangularBox(Box):
    dgs: DownGrades
    width = 1000
    height = 1000
    depth = 1000
    distance = 200
    floor = 100

    def top(self, p: g.Point):
        return self.height + self.floor - p.z

    def right(self, p: g.Point):
        return self.width / 2 - p.x

    def left(self, p: g.Point):
        return p.x - self.width / 2

    def bottom(self, p: g.Point):
        return p.z - self.floor



