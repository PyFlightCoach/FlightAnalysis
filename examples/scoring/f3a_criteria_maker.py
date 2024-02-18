from flightanalysis.scoring.criteria import *
import numpy as np


f3a=dict(
    single=dict(
        track=Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 100)),
        roll=Single(Exponential.fit_points(np.radians([30, 90]), [1, 6], 100)),
        angle=Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 100)),
        distance = Single(Exponential.fit_points([20, 40], [0.5, 1]))
    ),
    intra=dict(
        track=ContAbs(Exponential.fit_points(np.radians([30, 90]), [2, 6])),
        roll=ContAbs(Exponential.fit_points(np.radians([30, 90]), [1.5, 6])),
        radius=ContRat(Exponential.fit_points([1,5], [0.5, 4], 2)),
        speed=ContRat(Exponential.fit_points([1,5], [0.15, 0.75], 1)),
        roll_rate=ContRat(Exponential.fit_points([1,5], [0.15, 0.75], 1)),
        stallturn_speed=InsideBound(Exponential.fit_points([2, 5], [0.3,1.5]), [-2,2]),
        stallturn_width=InsideBound(Exponential.fit_points([2, 5], [0.5,2.5]), [-2,2]),
        spin_entry_length=InsideBound(Exponential.fit_points([2, 5], [0.3,1.5]), [-5,5]),
        pitch_break_length=InsideBound(Exponential.fit_points([1, 2], [0.5,2.5]), [-2,2]),
        recovery_length=MaxBound(Exponential.fit_points([1, 2], [0.5,2.5]), 2),
    ),
    inter=dict(
        radius=Comparison(Exponential.fit_points([1,5], [1, 2], 2)),
        speed=Comparison(Exponential.fit_points([1,5], [0.25, 1.0])),
        roll_rate=Comparison(Exponential.fit_points([1,5], [0.25, 1.5],2)),
        length=Comparison(Exponential.fit_points([1,5], [1, 3], 3)),
        free=Comparison(free),
    )
)


if __name__ == "__main__":

    with open('examples/scoring/temp.py', 'w') as f:
        for group, v in f3a.items():
            f.write(f'class F3A{group.capitalize()}:\n')
            for n, crit in v.items():
                f.write(f'    {n}={crit.to_py()}\n')

