from flightdata import State
import geometry as g

from .measurement import Measurement, measures as m


@m.add
def speed(fl: State, tp: State) -> Measurement:
    value = abs(fl.vel)
    return Measurement(
        value,
        "m/s",
        *Measurement._vector_vis(fl.att.transform_point(fl.vel).unit(), fl.pos),
    )

@m.add
def vertical_speed(fl: State, tp: State) -> Measurement:
    body_direction = fl.att.inverse().transform_point(g.PZ())
    return Measurement(
        g.Point.scalar_projection(fl.vel, body_direction),
        "m/s",
        *Measurement._vector_vis(
            fl.att.transform_point(g.PZ()).unit(), fl.pos
        ),
    )