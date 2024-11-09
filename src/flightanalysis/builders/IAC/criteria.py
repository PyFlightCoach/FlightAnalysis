from flightanalysis.scoring.criteria import (
    Single,
    Limit,
    Peak, Trough,
    Exponential,
    Continuous,
    ContinuousValue,
    Bounded,
    Comparison,
    free,
)
import numpy as np


class IACIntra:
    angle = Single(Exponential.fit_points(np.radians([30, 90]), [3, 9], 10))
    end_track = Single(Exponential.fit_points(np.radians([30, 90]), [3, 9], 10))
    end_roll = Single(Exponential.fit_points(np.radians([30, 90]), [2, 9], 10))
    track = Continuous(Exponential.fit_points(np.radians([30, 90]), [3, 9], 10))
    roll = Continuous(Exponential.fit_points(np.radians([30, 90]), [2, 9], 10))
    
    loopshape = Continuous(Exponential.fit_points([1.5, 3], [0.5, 1], 3))
    loopsmoothness = ContinuousValue(Exponential.fit_points([1, 2], [0.25, 0.7], 3))

    rollrate = Continuous(Exponential.fit_points([1, 3], [0.2, 0.6], 3))
    rollsmoothness = ContinuousValue(Exponential.fit_points([1, 2], [0.25, 0.7], 3))

    autorotation_rate = Continuous(Exponential.fit_points([1, 3], [0.02, 0.06], 0.5))
    stallturn_speed = Limit(Exponential.fit_points([10, 20], [0.5, 1.0], 1), 15)
    stallturn_width = Peak(Exponential.fit_points([20, 50], [0.25, 1.25], 10), 10)
    break_pitch_rate = Bounded(Exponential(10, 1, 0.1), 0.6, -0.6)
    peak_break_pitch_rate = Trough(Exponential(10, 1, 6), limit=0.6)
    
    autorotation_alpha = Bounded(Exponential(20, 1, 10), np.radians(7.5), -np.radians(7.5))
    pos_autorotation_alpha = Bounded(Exponential(20, 1, 10), np.radians(7.5))
    neg_autorotation_alpha = Bounded(Exponential(20, 1, 10), None, -np.radians(7.5))
    drop_pitch_rate = Bounded(Exponential(10, 1, 0.1), 0.2)
    peak_drop_pitch_rate = Trough(Exponential(10, 1, 10), 0.2)
    recovery_roll_rate = Bounded(Exponential(1, 1, 0.01), np.pi * 2, -np.pi*2)
    box = Bounded(Exponential.fit_points([50, 100], [0.5, 1], 10), 0, None)
    btmbox = Bounded(Exponential.fit_points([50, 100], [5, 10], 10), 0, None)

class IACInter:
    radius = Comparison(Exponential.fit_points([1, 2], [1, 2], 2))
    speed = Comparison(free)
    roll_rate = Comparison(Exponential.fit_points([1, 2], [0.25, 0.5], 1))
    length = Comparison(Exponential.fit_points([1, 2], [1, 2], 2))
    free = Comparison(free)


class IAC:
    inter = IACInter
    intra = IACIntra


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
    plot_all(IACIntra)
