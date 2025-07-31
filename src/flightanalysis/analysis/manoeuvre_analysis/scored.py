from __future__ import annotations
from dataclasses import dataclass
from flightanalysis import ManParm, ManoeuvreResults, Result
from more_itertools import flatten
from .complete import Complete
import geometry as g


@dataclass(repr=False)
class Scored(Complete):
    scores: ManoeuvreResults

    def downgrade(self) -> Complete:
        return Complete(
            self.id,
            self.schedule_direction,
            self.flown,
            self.mdef,
            self.manoeuvre,
            self.template,
        )

    @staticmethod
    def from_dict(ajman: dict) -> Scored:
        analysis = Complete.from_dict(ajman)
        if (
            isinstance(analysis, Complete)
            and "scores" in ajman
            and ajman["scores"] is not None
        ):
            return Scored(
                **analysis.__dict__, scores=ManoeuvreResults.from_dict(ajman["scores"])
            )
        else:
            return analysis

    def to_dict(self, basic: bool = False) -> dict:
        _basic = super().to_dict(
            basic
        )  # , sinfo, dict(**history, **self.fcj_results()))
        if basic:
            return _basic
        return dict(**_basic, scores=self.scores.to_dict())

    def fcj_results(self):
        return dict(
            els=[
                dict(name=k, start=v.start, stop=v.stop)
                for k, v in self.flown.labels.element.labels.items()
            ],
            results=self.scores.fcj_results(),
        )

    def plot_inter(self, name_or_id: str | int, shifts: g.Point | None = None):
        from plotting import plotsec, resize_3d_fig
        import plotly.graph_objects as go
        res: Result = self.scores.inter[name_or_id]
        if shifts is None:
            shifts = g.P0(len(res.dgs))

        mp: ManParm = self.mdef.mps[name_or_id]
        el_groups = [[co.elname for co in so.list_parms()] for so in mp.collectors]
        all_els = list(flatten(el_groups))
#        els = [k.split(".")[0] for k in res.measurement.keys]

        fig: go.Figure = plotsec(
            [fl for fl in self.flown.element],
            color=["red" if el.uid in all_els else "rgba(0, 0, 0, 0.2)" for el in self.manoeuvre.elements],
            ribb=True, tips=False, cg=True, nmodels=2, line=dict(width=5), scale=10, modelscale=1
        ).update_layout(    
            width=600,
            height=400,
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
            )
        )


        annotations = []

        for i, els in enumerate(el_groups):
            st0 = self.flown.element[slice(els[0], els[-1])]
            els = [self.manoeuvre.elements[el] for el in els]
            
            pos = st0.pos[len(st0)//2]
            annotations.append(
                dict(
                    x=pos.x[0],
                    y=pos.y[0],
                    z=pos.z[0],
                    ax=shifts.x[i],
                    ay=shifts.y[i],
                    #zshift=shifts.z[i],
                    showarrow=True,
                    arrowsize=2,
                    arrowwidth=1,
                    arrowhead=2,
                    text=f"{els[0].__class__.__name__} {i+1}",
                    font=dict(size=20, color="black", family="Rockwell"),
                )
            )

        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(
                annotations = annotations,
                camera=dict(projection=dict(type="orthographic"))
                
            )
        )

        fig = resize_3d_fig(fig, width=600)
        return fig