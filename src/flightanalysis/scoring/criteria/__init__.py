from __future__ import annotations
import numpy as np

from .exponential import Exponential, free
from .criteria import Criteria
from .inter.combination import Combination
from .inter.comparison import Comparison
from .intra.bounded import Bounded
from .intra.continuous import Continuous, ContinuousValue
from .intra.peak import Peak, Trough, AbsPeak, AbsTrough
from .intra.single import Limit, Single, Threshold
from .intra.deviation import Deviation, Total
from .criteria_group import CriteriaGroup


type AnyInterCriteria = Combination | Comparison

type AnyIntraCriteria = (
    Bounded
    | Continuous
    | ContinuousValue
    | Peak
    | Trough
    | AbsPeak
    | AbsTrough
    | Limit
    | Single
    | Threshold
    | Deviation
    | Total
    | CriteriaGroup
)

from .parser import parse_criteria_csv

def plot_lookup(lu, v0=0, v1=10):
    import plotly.express as px

    x = np.linspace(v0, v1, 30)
    px.line(x=x, y=lu(x)).show()


def plot_all(crits: CriteriaGroup):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # crits = {k: getattr(crits, k) for k in dir(crits) if not k.startswith("__")}
    # names = [f'{k}_{cr}' for k, crit in crits.items() for cr in crit.keys()]

    ncols = 4
    fig = make_subplots(
        int(np.ceil(len(crits) / ncols)),
        ncols,
        subplot_titles=list(crits.keys()),
        vertical_spacing=0.05,
    )

    for i, crit in enumerate(crits):
        fig.add_trace(
            crit.lookup.trace(showlegend=False), row=1 + i // ncols, col=1 + i % ncols
        )
    return fig


