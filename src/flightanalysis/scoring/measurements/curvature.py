from flightdata import State
import geometry as g
import numpy as np
import pandas as pd
from .measurement import Measurement, measures as m


@m.add
def curvature(fl: State, tp: State, proj: g.Point) -> Measurement:
    """
    Ratio error in curvature, direction is a vector in the axial direction
    proj is the ref_frame(tp[0]) axial direction
    """
    wproj = tp[0].att.transform_point(proj)
    with np.errstate(invalid="ignore"):
        flc, tpc = fl.curvature(wproj), tp.curvature(wproj)
        rat = g.point.scalar_projection(flc, tpc)

    return Measurement(
        Measurement.ratio(rat, abs(tpc)),
        "ratio",
        *Measurement._rad_vis(fl.pos, wproj),
    )


@m.add
def curvature_proj(fl: State, tp: State) -> Measurement:
    return curvature(fl, tp, Measurement.get_axial_direction(tp))


@m.add
def absolute_curvature(fl: State, tp: State, proj: g.Point) -> Measurement:
    wproj = tp[0].att.transform_point(proj)
    with np.errstate(invalid="ignore"):
        flc, tpc = fl.curvature(wproj), tp.curvature(wproj)
        rat = g.point.scalar_projection(flc, tpc) / abs(tpc)

    return Measurement(
        rat,
        "1",
        *Measurement._rad_vis(fl.pos, wproj),
    )


@m.add
def absolute_curvature_proj(fl: State, tp: State) -> Measurement:
    return absolute_curvature(fl, tp, Measurement.get_axial_direction(tp))
