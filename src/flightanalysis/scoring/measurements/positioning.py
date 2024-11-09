from flightdata import State
import geometry as g
import numpy as np

from .measurement import Measurement, measures as m


@m.add
def depth(fl: State, tp: State) -> Measurement:
    return Measurement(fl.pos.y, "m", *Measurement.depth_vis(fl.pos))


@m.add
def side_box(fl: State, tp: State):
    return Measurement(
        np.arctan(fl.pos.x / fl.pos.y), "rad", *Measurement.lateral_pos_vis(fl.pos)
    )


@m.add
def top_box(fl: State, tp: State):
    return Measurement(
        np.arctan(fl.pos.z / fl.pos.y),
        "rad",
        fl.pos,
        np.full(len(fl), 0.5),  # top box is always hard to tell
    )


@m.add
def centre_box(fl: State, tp: State):
    return Measurement(
        np.arctan(fl.pos.x / fl.pos.y), "rad", *Measurement.lateral_pos_vis(fl.pos)
    )






