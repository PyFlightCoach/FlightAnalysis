from .exponential import Exponential, free
from .criteria import Criteria
from .intra.single import Single, Limit, Threshold
from .intra.peak import Peak, Trough
from .intra.continuous import Continuous, ContinuousValue
from .intra.bounded import Bounded
from .inter.comparison import Comparison
from .inter.combination import Combination

import numpy as np


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
    ncols = 4
    fig = make_subplots(
        int(np.ceil(nplots / ncols)), ncols, subplot_titles=list(crits.keys())
    )

    for i, crit in enumerate(crits.values()):
        fig.add_trace(
            crit.lookup.trace(showlegend=False), row=1 + i // ncols, col=1 + i % ncols
        )
    fig.show()
