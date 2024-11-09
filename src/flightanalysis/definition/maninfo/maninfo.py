from .positioning import Position, BoxLocation
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ManInfo:
    name: str
    short_name: str
    k: float
    position: Position
    start: BoxLocation
    end: BoxLocation
    centre_points: list[int] = field(
        default_factory=lambda: []
    )  # points that should be centered, ids correspond to the previous element
    centred_els: list[Tuple[int, float]] = field(
        default_factory=lambda: []
    )  # element ids that should be centered

    def to_dict(self):
        return dict(
            name=self.name,
            short_name=self.short_name,
            k=self.k,
            position=self.position.name,
            start=self.start.to_dict(),
            end=self.end.to_dict(),
            centre_points=self.centre_points,
            centred_els=self.centred_els,
        )

    @staticmethod
    def from_dict(inp: dict):
        return ManInfo(
            inp["name"],
            inp["short_name"],
            inp["k"],
            Position[inp["position"]],
            BoxLocation.from_dict(inp["start"]),
            BoxLocation.from_dict(inp["end"]),
            inp["centre_points"],
            inp["centred_els"],
        )

