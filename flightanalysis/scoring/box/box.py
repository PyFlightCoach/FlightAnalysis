from __future__ import annotations
import numpy as np
from dataclasses import dataclass
import geometry as g
from flightanalysis.scoring import (
    Bounded,
    Single,
    Result,
    Measurement,
    Criteria,
    Results,
)
from flightanalysis.definition.maninfo import ManInfo
from flightdata import State
from typing import Literal, Tuple
import numpy.typing as npt
from ..visibility import visibility

T = Tuple[g.Point, npt.NDArray]


@dataclass
class BoxDG:
    criteria: Bounded
    unit: Literal["m", "rad"]

    def to_dict(self):
        return dict(criteria=self.criteria.to_dict(), unit=self.unit)


@dataclass
class Box:
    #    dgs: ClassVar = ["top", "bottom", "left", "right", "front", "back", "centre"]
    width: float
    height: float
    depth: float
    distance: float
    floor: float
    bound_dgs: dict[str, BoxDG]
    centre_criteria: Single = None
    relax_back: bool = False

    def to_dict(self):
        return dict(
            Kind=self.__class__.__name__,
            width=self.width,
            height=self.height,
            depth=self.depth,
            distance=self.distance,
            floor=self.floor,
            bound_dgs={k: v.to_dict() for k, v in self.bound_dgs.items()},
            centre_criteria=self.centre_criteria.to_dict() if self.centre_criteria else None,
            relax_back=self.relax_back,
        )


    @classmethod
    def from_dict(Cls, data):
        return {C.__name__: C for C in Cls.__subclasses__()}[data.pop("Kind")](
            bound_dgs={
                k: BoxDG(Criteria.from_dict(v["criteria"]), v["unit"])
                for k, v in data.pop("bound_dgs").items()
            },
            centre_criteria=Criteria.from_dict(data.pop("centre_criteria")),
            relax_back=data.pop("relax_back"),  
            **data,
        )

    def top(self, p: g.Point) -> T:
        raise NotImplementedError

    def right(self, p: g.Point) -> T:
        raise NotImplementedError

    def left(self, p: g.Point) -> T:
        raise NotImplementedError

    def bottom(self, p: g.Point) -> T:
        raise NotImplementedError

    def front(self, p: g.Point) -> T:
        return g.PY(-1), p.y - self.distance

    def back(self, p: g.Point) -> T:
        return g.PY(1), self.distance + self.depth - p.y

    def score(self, info: ManInfo, fl: State, tp: State):
        res = Results("positioning")

        if self.centre_criteria:
            m = Measurement(
                self.centre_angle(fl.pos)[1],
                "rad",
                *Measurement.lateral_pos_vis(fl.pos),
            )
            sample = visibility(
                m.value, m.visibility, self.centre_criteria.lookup.error_limit
            )
            els = fl.label_ranges(["element"])

            ovs = []
            for cpid in info.centre_points:
                ovs.append(int(els.start.iloc[cpid]))

            for ceid, fac in info.centred_els:
                ce = fl.get_element(els.iloc[ceid, 0])
                path_length = (abs(ce.vel) * ce.dt).cumsum()
                id = np.abs(path_length - path_length[-1] * fac).argmin()
                ovs.append(int(id + els.iloc[ceid].start))

            res.add(
                Result(
                    "centre_box",
                    m,
                    sample[ovs],
                    ovs,
                    *self.centre_criteria(sample[ovs], True),
                    self.centre_criteria,
                )
            )

        for k, dg in self.bound_dgs.items():
            if self.relax_back and k == "back":
                if (tp.pos.y.max() - tp.pos.y.min()) > 20:
                    continue
            direction, vs = getattr(self, f'{k}{"_angle" if dg.unit=='rad' else ""}')(
                fl.pos
            )
            
            m = Measurement(
                vs,
                dg.unit,
                *Measurement.lateral_pos_vis(fl.pos)
                if dg.unit == "rad"
                else Measurement._vector_vis(g.Point.full(direction, len(fl)), fl.pos),
            )
            sample = visibility(
                dg.criteria.prepare(m.value),
                m.visibility,
                dg.criteria.lookup.error_limit,
            )
            res.add(
                Result(
                    f"{k}_box",
                    m,
                    sample,
                    np.arange(len(fl)),
                    *dg.criteria(sample, True),
                    dg.criteria,
                )
            )

        return res
