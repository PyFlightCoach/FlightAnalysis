from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from flightdata import Collection
from flightdata.base import to_list
from flightanalysis.scoring.measurement import Measurement
from dataclasses import dataclass


@dataclass
class Result:
    """
    Intra - this Result covers the downgrades applicable to things like the change of radius within an element.
    Inter - This result covers the downgrades applicable to a set of loop diameters within a manoevre (one ManParm)
    """
    name: str
    measurement: Measurement 
    sample: npt.NDArray  # the comparison built from the measurement
    errors: npt.NDArray  # the errors resulting from the comparison
    dgs: npt.NDArray # downgrades for the errors
    keys: npt.NDArray # links from dgs to sample index

    @property
    def total(self):
        return float(sum(self.dgs))
    
    def to_dict(self):
        return dict(
            name = self.name,
            measurement = self.measurement.to_dict() if isinstance(self.measurement, Measurement) else list(self.measurement),
            sample=to_list(self.sample),
            errors=to_list(self.errors),
            dgs=to_list(self.dgs),
            keys=to_list(self.keys),
            total=self.total
        )
    
    def __repr__(self):
        return f'Result({self.name}, {self.total})'
    
    @staticmethod
    def from_dict(data) -> Result:
        return Result(
            data['name'],
            Measurement.from_dict(data['measurement']) if isinstance(data['measurement'], dict) else np.array(data['measurement']),
            np.array(data['sample']),
            np.array(data['errors']),
            np.array(data['dgs']),
            np.array(data['keys'])
        )

    def info(self, i: int):
        return f'downgrade={np.round(self.dgs[i], 3)}\nerror={np.round(self.errors[i],3)}\nvisibility={np.round(self.measurement.visibility[self.keys[i]], 2)}'

    def summary_df(self):
        return pd.DataFrame(
            np.column_stack([self.keys, self.sample, self.errors, self.measurement.visibility, self.dgs]),
            columns = ['collector', 'value', 'error', 'visibility', 'downgrade']
        )

    def plot(self):
        import plotly.graph_objects as go
        fig=go.Figure(layout=dict(
            yaxis=dict(title='measurement', range=[0,np.max(self.sample)*2]), 
            yaxis2=dict(title='visibility', overlaying="y", range=[0,1])
        ))
        
        x=list(range(0, len(self.measurement),1))
        fig.add_trace(go.Scatter(x=x,y=self.measurement.value, name='flown'))

        fig.add_trace(go.Scatter(
            x=x, y=self.sample, 
            name='sample', yaxis='y',
            line=dict(width=3, color='black')
        ))

        hovtxt=[self.info(i) for i in range(len(self.keys))]

        fig.add_trace(go.Scatter(
            x=self.keys, y=self.sample[self.keys],
            text=np.round(self.dgs, 3),
            hovertext=hovtxt,
            mode='markers+text',
            name='downgrades',
            yaxis='y'
        ))

        fig.add_trace(go.Scatter(
            x=x, y=self.measurement.visibility, name='visibility',yaxis='y2'))

        return fig
    
class Results(Collection):
    """
    Intra - the Results collection covers all the downgrades in one element
    Inter - the Results collection covers all the downgrades in one Manoeuvre
    """
    VType = Result
    uid="name"

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    @property
    def total(self):
        return sum([cr.total for cr in self])

    def downgrade_summary(self):
        return {r.name: r.dgs for r in self if len(r.dgs) > 0}

    def downgrade_df(self) -> pd.DataFrame:
        dgs = self.downgrade_summary()
        if len(dgs) == 0:
            return pd.DataFrame()
        max_len = max([len(v) for v in dgs.values()])
        def extend(vals):
            return [vals[i] if i < len(vals) else np.NaN for i in range(max_len)]
        df =  pd.DataFrame.from_dict({k:extend(v) for k,v in dgs.items()})
        
        return df

    def to_dict(self) -> dict[str, dict]:
        return dict(
            name = self.name,
            data = {k: v.to_dict() for k, v in self.data.items()},
            total = self.total
        )

    @staticmethod
    def from_dict(data) -> Results:
        return Results(
            data['name'],
            [Result.from_dict(v) for v in data['data'].values()]
        )


class ElementsResults(Collection):
    """Intra Only
    Elements Results covers all the elements in a manoeuvre
    """
    VType=Results
    uid="name"

    @property
    def total(self):
        return sum([r.total for r in self])
    
    @property
    def downgrade_list(self):
        return [r.total for r in self]
    
    def downgrade_df(self):
        df = pd.concat([idg.downgrade_df().sum() for idg in self], axis=1).T
        df = pd.concat([df, pd.DataFrame(df.sum()).T])#(np.floor(df.sum())).T])
        df.index = list(self.data.keys()) + ['Total']
        
        return df
    
    def to_dict(self) -> dict[str, dict]:
        return dict(
            data = {k: v.to_dict() for k, v in self.data.items()},
            summary = self.downgrade_list,
            total = float(self.total)
        )

    @staticmethod
    def from_dict(data) -> Results:
        return ElementsResults(
            {k: Results.from_dict(v) for k, v in data['data'].items()}
        )


@dataclass
class ManoeuvreResults:
    inter: Results
    intra: ElementsResults
    positioning: Results

    def summary(self):
        return {k: v.total for k, v in self.__dict__.items() if v is not None} 

    def score(self):
        return max(0, 10 - sum([v for v in self.summary().values()]))
    
    def to_dict(self):
        return dict(
            inter=self.inter.to_dict(),
            intra=self.intra.to_dict(),
            positioning=self.positioning.to_dict(),
            summary=self.summary(),
            score=self.score()
        )

    @staticmethod
    def from_dict(data):
        return ManoeuvreResults(
            Results.from_dict(data['inter']),
            ElementsResults.from_dict(data['intra']),
            Results.from_dict(data['positioning']),
        )