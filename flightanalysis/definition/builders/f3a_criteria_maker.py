from flightanalysis.scoring.criteria import Single, Exponential, ContAbs, ContRat, InsideBound, MaxBound, Comparison, free, OutsideBound
from flightanalysis.definition.builders.schedules.create_all import create_all
import numpy as np


f3a=dict(
    single=dict(
        track=Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 6)),
        roll=Single(Exponential.fit_points(np.radians([30, 90]), [1, 6], 6)),
        angle=Single(Exponential.fit_points(np.radians([30, 90]), [2, 6], 6)),
    ),
    intra=dict(
        track=ContAbs(Exponential.fit_points(np.radians([30, 90]), [2, 6], 6), 5),
        roll=ContAbs(Exponential.fit_points(np.radians([30, 90]), [1.5, 6], 6), 10),
        radius=ContRat(Exponential.fit_points([1,2], [0.5, 1], 1), 60),
        speed=ContRat(Exponential.fit_points([1,5], [0.15, 0.75], 1), 5),
        roll_rate=ContRat(Exponential.fit_points([1,3], [0.3, 0.9], 0.5), 60),
        autorotation_rate=ContRat(Exponential.fit_points([1,3], [0.3, 0.9], 0.5), 5),
        stallturn_speed=InsideBound(Exponential.fit_points([2, 5], [0.3,1.5]), [-2,2]),
        stallturn_width=InsideBound(Exponential.fit_points([2, 5], [0.5,2.5]), [-2,2]),
        spin_entry_length=InsideBound(Exponential.fit_points([2, 5], [0.3,1.5]), [-5,5]),
        pitch_break_length=InsideBound(Exponential.fit_points([1, 2], [0.7,3.5]), [-2,2]),
        nose_drop_amount=OutsideBound(Exponential(20,1), [-np.radians(15), np.radians(15)]),
        recovery_length=MaxBound(Exponential.fit_points([1, 2], [0.7,3.5]), 2),
        box=InsideBound(Exponential(10/np.radians(7.5), 1), [-np.radians(60), np.radians(60)]), # 10 points if the entire manoeuvre is 7.5 degrees outside the box
        depth=MaxBound(Exponential.fit_points([20, 40], [0.5, 1]), 170)
    ),
    inter=dict(
        radius=Comparison(Exponential.fit_points([1,2], [1, 2], 2)),
        speed=Comparison(free),
        roll_rate=Comparison(Exponential.fit_points([1,2], [0.25, 0.5], 1)),
        length=Comparison(Exponential.fit_points([1,2], [1, 2], 2)),
        free=Comparison(free),
    )
)


def dump_criteria_to_py(criteria):
    file = 'flightanalysis/scoring/criteria/f3a_criteria.py'
    with open(file, 'r') as f:
        lines = f.readlines()
    first_line = lines.index('### Generated code ###\n')
    last_line = lines.index('### End Generated code ###\n')
    

    with open(file, 'w') as f:

        f.writelines(lines[:first_line+1])
        for group, v in criteria.items():
            f.write(f'class F3A{group.capitalize()}:\n')
            for n, crit in v.items():
                f.write(f'    {n}={crit.to_py()}\n')
        f.writelines(lines[last_line:])

def plot_lookup(lu, v0=0, v1=10):
    import plotly.express as px
    x = np.linspace(v0, v1, 30)
    px.line(x=x,y=lu(x)).show()

def plot_all(crits):
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    criteria = [cr for crit in crits.values() for cr in crit.values()]
    names = [f'{k}_{cr}' for k, crit in crits.items() for cr in crit.keys()]

    nplots = sum([len(cr) for cr in crits.values()])
    ncols=7
    fig = make_subplots(int(np.ceil(nplots / ncols)), ncols, subplot_titles=names)
    
    for i, crit in enumerate(criteria):
        row, col = 1 + i // ncols, 1 + i % ncols
        x = np.linspace(0, 10, 30)
        fig.add_trace(go.Scatter(x=x, y=crit.lookup(x), showlegend=False), row=row, col=col)
    fig.show()

if __name__ == "__main__":
    #plot_lookup(f3a['intra']['recovery_length'].lookup,-10,10)

#    plot_all(f3a)
    dump_criteria_to_py(f3a)
    create_all()