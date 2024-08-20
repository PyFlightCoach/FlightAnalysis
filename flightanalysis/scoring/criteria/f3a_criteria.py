from flightanalysis.scoring.criteria import (
    Single,
    Limit,
    Peak,
    Exponential,
    Continuous,
    ContinuousValue,
    InsideBound,
    MaxBound,
    Comparison,
    OutsideBound,
    MinBound,
    free,
)
import numpy as np


class F3AIntra:
    angle = Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 6))
    end_track = Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 6))
    end_roll = Single(Exponential.fit_points(np.radians([30, 90]), [1, 6], 6))
    track =                 Continuous(   Exponential.fit_points(np.radians([30, 90]), [1.75, 6], 6),   4)
    roll =                  Continuous(   Exponential.fit_points(np.radians([30, 90]), [1.25, 6], 6),   1)
    radius =                Continuous(   Exponential.fit_points([1.5, 3], [0.5, 1], 1),                0.5)
    speed =            ContinuousValue(   Exponential.fit_points([5, 15], [0.03, 0.09], 0.5),           4)
    roll_rate =             Continuous(   Exponential.fit_points([1, 3], [0.02, 0.06], 0.5),            1)
    autorotation_rate =     Continuous(   Exponential.fit_points([1, 3], [0.02, 0.06], 0.5),            2)
    stallturn_speed =       Limit(        Exponential.fit_points([2, 4], [0.05, 0.1], 4),               4)
    stallturn_width =       Peak(         Exponential.fit_points([2, 5], [0.25, 1.25], 6),              2)
    break_pitch_rate =      OutsideBound( Exponential(10, 1, 6),                                        [-0.6, 0.6])
    autorotation_alpha =    OutsideBound( Exponential(20, 1, 6),                                        [-np.radians(7.5), np.radians(7.5)])
    drop_pitch_rate =       MinBound(     Exponential(10, 1, 6),                                        0.2)
    recovery_roll_rate =    MaxBound(     Exponential(1, 1, 0.01),                                        0)
    recovery_alpha_delta =  OutsideBound( Exponential(1, 1, 0.01),                                         [-0.2, 0.2])
    recovery_length =       MaxBound(     Exponential.fit_points([1, 2], [0.7, 3.5]),                   2)
    box =                   InsideBound(  Exponential(10 / np.radians(7.5), 1),                         [-np.radians(60), np.radians(60)])
    depth =                 MaxBound(     Exponential.fit_points([20, 40], [0.5, 1]),                   170)


class F3AInter:
    radius = Comparison(Exponential.fit_points([1, 2], [1, 2], 2))
    speed = Comparison(free)
    roll_rate = Comparison(Exponential.fit_points([1, 2], [0.25, 0.5], 1))
    length = Comparison(Exponential.fit_points([1, 2], [1, 2], 2))
    free = Comparison(free)


class F3A:
    inter = F3AInter
    intra = F3AIntra


def plot_lookup(lu, v0=0, v1=10):
    import plotly.express as px

    x = np.linspace(v0, v1, 30)
    px.line(x=x, y=lu(x)).show()


def plot_all(crits):
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    crits = {k: getattr(crits, k) for k in dir(crits) if not k.startswith("__")}
    # names = [f'{k}_{cr}' for k, crit in crits.items() for cr in crit.keys()]

    nplots = len(crits)
    ncols = 7
    fig = make_subplots(
        int(np.ceil(nplots / ncols)), ncols, subplot_titles=list(crits.keys())
    )

    for i, crit in enumerate(crits.values()):
        fig.add_trace(
            crit.lookup.trace(showlegend=False), row=1 + i // ncols, col=1 + i % ncols
        )
    fig.show()


if __name__ == "__main__":
    plot_all(F3AIntra)
