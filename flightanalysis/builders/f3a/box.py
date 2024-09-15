from flightanalysis.box import TriangularBox
from flightanalysis.scoring import DownGrades, DownGrade, Measurement, Result, Results
from flightanalysis.definition.maninfo import Position
from flightdata import State
from flightanalysis.builders.f3a.criteria import F3A
import numpy as np


box = TriangularBox(
    DownGrades([
        DownGrade("side_box", Measurement.side_box, None, None, F3A.intra.box, "side_box"),
        DownGrade("top_box", Measurement.top_box, None, None, F3A.intra.box, "top_box"),
        DownGrade("centre", Measurement.centre_box, None, None, F3A.intra.angle, "centre"),
        DownGrade("distance", Measurement.depth, None, None, F3A.intra.depth, "distance"),
    ]), 
    np.radians(120), 
    np.radians(60), 
    np.radians(25), 
    np.radians(150), 
    np.radians(15)
)



def create_centre_result(self, name: str, st: State) -> Result:
    meas = Measurement.centre_box(st)
    errors, dgs, keys = F3A.intra.angle(meas.value)
    return Result(
        name,
        meas,
        meas.value,
        np.arange(len(meas.value)),
        errors,
        dgs * meas.visibility[keys],
        keys,
        F3A.intra.angle,
    )


def centre(self):
    results = Results("centres")
    for cpid in self.mdef.info.centre_points:
        if cpid == len(self.manoeuvre.elements):
            st = self.manoeuvre.elements[-1].get_data(self.flown)[-1]
        else:
            st = self.manoeuvre.elements[cpid].get_data(self.flown)[0]
        results.add(self.create_centre_result(f"centre point {cpid}", st))

    for ceid, fac in self.mdef.info.centred_els:
        ce = self.manoeuvre.elements[ceid].get_data(self.flown)
        path_length = (abs(ce.vel) * ce.dt).cumsum()
        id = np.abs(path_length - path_length[-1] * fac).argmin()
        results.add(
            self.create_centre_result(
                f"centred element {ceid}", State(ce.data.iloc[[id], :])
            )
        )

    if len(results) == 0 and self.mdef.info.position == Position.CENTRE:
        al = State(
            self.flown.data.loc[
                (self.flown.data.element != "entry_line")
                & (self.flown.data.element != "exit_line")
            ]
        )
        midy = (np.max(al.y) + np.min(al.y)) / 2
        midid = np.abs(al.pos.y - midy).argmin()
        results.add(self.create_centre_result("centred manoeuvre", al[midid]))

    return results

