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


class F3AIntra:
    angle = Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 6))
    end_track = Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 6))
    end_roll = Single(Exponential.fit_points(np.radians([30, 90]), [1, 6], 6))
    track = Continuous(Exponential.fit_points(np.radians([30, 90]), [1.75, 6], 6))
    roll = Continuous(Exponential.fit_points(np.radians([30, 90]), [1.25, 6], 6))
    speed = ContinuousValue(Exponential.fit_points([5, 15], [0.1, 0.3], 0.5))
    roll_gradient = ContinuousValue(Exponential.fit_points([0.5, 1], [0.1, 0.2], 1))
    
    loopshape = Continuous(Exponential.fit_points([1.5, 3], [0.5, 1], 3))
    loopsmoothness = ContinuousValue(Exponential.fit_points([0.5, 1], [0.025, 0.05], 3))

    rollrate = Continuous(Exponential.fit_points([1, 3], [0.2, 0.6], 3))
    rollsmoothness = ContinuousValue(Exponential.fit_points([1, 2], [0.25, 0.7], 3))

    autorotation_rate = Continuous(Exponential.fit_points([1, 3], [0.02, 0.06], 0.5))
    stallturn_speed = Limit(Exponential.fit_points([2, 4], [0.5, 1.0], 1), 8)
    stallturn_width = Peak(Exponential.fit_points([2, 5], [0.25, 1.25], 6), 2)
    break_pitch_rate = Bounded(Exponential(10, 1, 0.1), 0.6, -0.6)
    peak_break_pitch_rate = Trough(Exponential(10, 1, 6), limit=0.6)
    
    autorotation_alpha = Bounded(
        Exponential(20, 1, 6), np.radians(7.5), -np.radians(7.5)
    )
    pos_autorotation_alpha = Bounded(Exponential(20, 1, 6), np.radians(7.5))
    neg_autorotation_alpha = Bounded(Exponential(20, 1, 6), None, -np.radians(7.5))
    drop_pitch_rate = Bounded(Exponential(10, 1, 0.1), 0.2)
    peak_drop_pitch_rate = Trough(Exponential(10, 1, 6), 0.2)
    recovery_roll_rate = Bounded(Exponential(1, 1, 0.01), np.pi * 2, -np.pi*2)
    box = Bounded(Exponential(10 / np.radians(7.5), 1, 2), None, 0)
    depth = Bounded(Exponential.fit_points([20, 40], [0.5, 1], 4), 0, None)


class F3AInter:
    radius = Comparison(Exponential.fit_points([2, 4], [0.3, 0.6], 2))
    speed = Comparison(free)
    roll_rate = Comparison(Exponential.fit_points([2, 4], [0.25, 0.5], 1))
    length = Comparison(Exponential.fit_points([1, 2], [0.6, 1.2], 2))
    free = Comparison(free)


class F3A:
    inter = F3AInter
    intra = F3AIntra



if __name__ == "__main__":
    from flightanalysis.scoring.criteria import plot_all, plot_lookup
    plot_all(F3AInter)
