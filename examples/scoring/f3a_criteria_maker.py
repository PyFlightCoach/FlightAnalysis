from flightanalysis.scoring.criteria import *
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from json import dump


f3a=dict(
    single=dict(
        track=Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 100), 'absolute'),
        roll=Single(Exponential.fit_points(np.radians([30, 90]), [1, 6], 100), 'absolute'),
        angle=Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 100), 'absolute'),
        distance=Single(Exponential.fit_points([20, 40], [0.5,1]), 'absolute')
    ),
    intra=dict(
        track=Continuous(Exponential.fit_points(np.radians([30, 90]), [2, 6]), 'absolute'),
        roll=Continuous(Exponential.fit_points(np.radians([30, 90]), [1.5, 6]), 'absolute'),
        radius=Continuous(Exponential.fit_points([1,5], [0.5, 4], 2), 'ratio'),
        speed=Continuous(Exponential.fit_points([1,5], [0.15, 0.75], 1), 'ratio'),
        roll_rate=Continuous(Exponential.fit_points([1,5], [0.15, 0.75], 1), 'ratio'),
    ),
    inter=dict(
        radius=Comparison(Exponential.fit_points([1,5], [1, 2], 2), 'ratio'),
        speed=Comparison(Exponential.fit_points([1,5], [0.25, 1.0]), 'ratio'),
        roll_rate=Comparison(Exponential.fit_points([1,5], [0.25, 1.5],2), 'ratio'),
        length=Comparison(Exponential.fit_points([1,5], [1, 3], 3), 'ratio'),
        free=Comparison(free, 'ratio'),
    )
)


if __name__ == "__main__":

    with open('examples/scoring/temp.py', 'w') as f:
        for group, v in f3a.items():
            f.write(f'class F3A{group.capitalize()}:\n')
            for n, crit in v.items():
                f.write(f'    {n}={crit.to_py()}\n')

