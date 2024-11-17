from __future__ import annotations
import numpy as np
from dataclasses import dataclass
import geometry as g
from flightanalysis.base.ref_funcs import RefFunc
from flightanalysis.scoring import (
    Bounded,
    Single,
    Result,
    Measurement,
    Criteria,
    Results,
    measures,
)
from schemas.maninfo import ManInfo
from flightdata import State
from typing import Literal, Tuple
import numpy.typing as npt
from ..visibility import visibility

T = Tuple[g.Point, npt.NDArray]


@dataclass
class BoxDG:
    criteria: Bounded
    measure: RefFunc = None

    def to_dict(self):
        return dict(
            criteria=self.criteria.to_dict(), measure=str(self.measure)
        )

    @staticmethod
    def from_dict(data):
        try:
            return BoxDG(
                criteria=Criteria.from_dict(data["criteria"]),
                measure=measures.parse(data["measure"]),
            )
        except Exception:
            return None

box_sides = [
    "top",
    "bottom",
    "left",
    "right",
    "front",
    "back",
]


@dataclass
class Box:
    #    dgs: ClassVar = ["top", "bottom", "left", "right", "front", "back", "centre"]
    width: float
    height: float
    depth: float
    distance: float
    floor: float
    bound_dgs: dict[str, BoxDG]
    centre_dg: BoxDG | None = None
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
            centre_dg=self.centre_dg.to_dict() if self.centre_dg else None,
            relax_back=self.relax_back,
        )

    @classmethod
    def from_dict(Cls, data):
        return {C.__name__: C for C in Cls.__subclasses__()}[data.pop("Kind")](
            bound_dgs={k: BoxDG.from_dict(v) for k, v in data.pop("bound_dgs").items()},
            centre_dg=BoxDG.from_dict(data.pop("centre_dg")) if "centre_dg" in data else None,
            relax_back=data.pop("relax_back"),
            **data,
        )

    def __getattr__(self, name: str):
        if name.endswith("_pos"):

            def pos(d_l: T) -> g.Point:
                return d_l[0] * d_l[1]

            return lambda p=None: pos(getattr(self, name.rsplit("_", 1)[0])(p))
        for s in box_sides:
            if name.startswith(s[:2]):
                parts = name.split("_")
                parts[0] = s

                def fun(p=None):
                    p = g.P0() if p is None else p
                    return getattr(self, "_" + "_".join(parts))(p)

                return fun
        raise AttributeError

    def middle(self):
        py = (self.back_pos() + self.front_pos()) / 2
        pz = (self.top_pos(py) + self.bottom_pos(py)) / 2
        return g.Point(0, py.y[0], pz.z[0])

    def _top(self, p: g.Point) -> T:
        raise NotImplementedError

    def _right(self, p: g.Point) -> T:
        raise NotImplementedError

    def _left(self, p: g.Point) -> T:
        raise NotImplementedError

    def _bottom(self, p: g.Point) -> T:
        raise NotImplementedError

    def _front(self, p: g.Point) -> T:
        p = g.P0() if p is None else p
        return g.PY(-1), p.y - self.distance

    def _back(self, p: g.Point) -> T:
        p = g.P0() if p is None else p
        return g.PY(1), self.distance + self.depth - p.y

    def score(self, info: ManInfo, fl: State, tp: State):
        res = Results("positioning")

        if self.centre_dg:
            m = self.centre_dg.measure(fl, tp, self)

            sample = visibility(
                m.value, m.visibility, self.centre_dg.criteria.lookup.error_limit
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
                    None,
                    sample,
                    ovs,
                    *self.centre_dg.criteria(sample[ovs], True),
                    self.centre_dg,
                )
            )

        for k, dg in self.bound_dgs.items():
            if self.relax_back and k == "back":
                if (tp.pos.y.max() - tp.pos.y.min()) > 20:
                    continue

            m: Measurement = dg.measure(fl, tp, self)

            sample = visibility(
                dg.criteria.prepare(m.value),
                m.visibility,
                dg.criteria.lookup.error_limit,
            )
            res.add(
                Result(
                    f"{k}_box",
                    m,
                    None,
                    sample,
                    np.arange(len(fl)),
                    *dg.criteria(sample, True),
                    dg.criteria,
                )
            )

        return res

    def corners(self):
        f = self.front_pos()
        b = self.back_pos()
        return g.Point(
            [
                [self.le_pos(f).x[0], f.y[0], self.bo_pos(f).z[0]],
                [self.ri_pos(f).x[0], f.y[0], self.bo_pos(f).z[0]],
                [self.le_pos(f).x[0], f.y[0], self.to_pos(f).z[0]],
                [self.ri_pos(f).x[0], f.y[0], self.to_pos(f).z[0]],
                [self.le_pos(b).x[0], b.y[0], self.bo_pos(f).z[0]],
                [self.ri_pos(b).x[0], b.y[0], self.bo_pos(f).z[0]],
                [self.le_pos(b).x[0], b.y[0], self.to_pos(b).z[0]],
                [self.ri_pos(b).x[0], b.y[0], self.to_pos(b).z[0]],
            ]
        )

    def face_front(self):
        return dict(i=[0, 1], j=[1, 3], k=[2, 2])

    def face_back(self):
        return dict(i=[4, 5], j=[5, 7], k=[6, 6])

    def face_bottom(self):
        return dict(i=[0, 1], j=[1, 5], k=[4, 4])

    def face_top(self):
        return dict(i=[2, 6], j=[3, 3], k=[6, 7])

    def face_left(self):
        return dict(i=[0, 2], j=[4, 4], k=[2, 6])

    def face_right(self):
        return dict(i=[1, 3], j=[5, 5], k=[3, 7])

    def plot(self):
        import plotly.graph_objects as go
        from plotting import pointtrace

        corners = self.corners()
        meshopts = dict(opacity=0.2, showlegend=False)

        return [
            pointtrace(
                corners,
                text=np.arange(len(corners)),
                mode="markers",
                marker=dict(size=1, color="black"),
                hoverinfo="skip",
            ),
            pointtrace(
                g.P0(),
                text="Pilot" if self.__class__.__name__ == "TriangularBox" else "Judge",
                mode="markers+text",
                marker=dict(size=2, color="black"),
            ),
            go.Mesh3d(
                **corners.to_dict(), **self.face_front(), color="mediumaquamarine", **meshopts
            ),
            go.Mesh3d(
                **corners.to_dict(), **self.face_back(), color="mediumaquamarine", **meshopts
            ),
            go.Mesh3d(
                **corners.to_dict(), **self.face_left(), color="mediumturquoise", **meshopts
            ),
            go.Mesh3d(
                **corners.to_dict(), **self.face_right(), color="mediumturquoise", **meshopts
            ),
            go.Mesh3d(
                **corners.to_dict(), **self.face_top(), color="dimgray", **meshopts
            ),
        #    go.Mesh3d(
        #        **corners.to_dict(), **self.face_bottom(), color="grey", **meshopts
        #    ),
        ]
