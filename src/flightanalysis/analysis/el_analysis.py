from __future__ import annotations
import numpy as np

from flightanalysis.scoring.results import Results, Result
from flightdata import State
from typing import Self
from flightanalysis import ElDef, Element, ManParms
from dataclasses import dataclass
import geometry as g


@dataclass
class ElementAnalysis:
    edef: ElDef
    mps: ManParms
    el: Element
    fl: State
    tp: State
    ref_frame: g.Transformation
    results: Results | None = None

    def update(self, new_fl: State):
        new_el = self.el.match_intention(self.ref_frame, new_fl)
        new_tp = new_el.create_template(self.tp[0], new_fl.time)
        return ElementAnalysis(
            self.edef, self.mps, new_el, new_fl, new_tp, self.ref_frame
        )

    def plot_3d(self, **kwargs):
        from plotting import plotsec

        return plotsec(dict(fl=self.fl, tp=self.tp), **kwargs)

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.__dict__.items()}

    @staticmethod
    def from_dict(data) -> Self:
        mps = ManParms.from_dict(data["mps"])
        return ElementAnalysis(
            ElDef.from_dict(data["edef"], mps),
            mps,
            Element.from_dict(data["el"]),
            State.from_dict(data["fl"]),
            State.from_dict(data["tp"]),
            g.Transformation.from_dict(data["ref_frame"]),
        )

    def score_dg(self, dg: str, limits: bool = True, select: bool = True) -> Result:
        return self.edef.dgs[dg](self.el, self.fl, self.tp, limits, select)

    def intra_score(self, limits: bool = True) -> Results:
        return self.edef.dgs.apply(
            self.el, self.fl, self.tp, limits
        )

    def info(self):
        return dict(
            element=self.el.uid,
            **(dict(angle=np.degrees(self.el.angle)) if "angle" in self.el.parameters else {}), 
            **(dict(radius=self.el.radius) if "radius" in self.el.parameters else {}),
            **(dict(rolls=np.degrees(self.el.rolls)) if "rolls" in self.el.parameters else {}),
            **(dict(roll=np.degrees(self.el.roll)) if "roll" in self.el.parameters else {}),
            freq=f"{1 / self.fl.dt.mean():.0f}",
            len=len(self.fl),
            **(dict(intra=f"{self.results.total:.4f}") if self.results is not None else {}),
        )  # fmt: skip

    def full_result_plot(self, name: str, showlegend=True, textposition: str = "bottom left"):
        """plot the actual result and the uncropped result on the same figure,
        include some info from the ddowngrade"""
        import plotly.graph_objects as go

        dg = self.edef.dgs[name]
        full_res: Result = dg(self.el, self.fl, self.tp, True, select=False)
        crop_res: Result = dg(self.el, self.fl, self.tp, True, select=True)
        full_xvals = self.fl.t - self.fl.t[0]
        crop_xvals = np.array(g.utils.get_value(full_xvals, crop_res.sample_keys))

        u = full_res.plot_f

        fig = go.Figure(
            layout=dict(
                yaxis2=dict(
                    title="Visibility", overlaying="y", range=[0, 1], side="right"
                ),
                title=f"{crop_res.name}, {crop_res.total:.2f}",
                legend=dict(orientation="h", x=0, y=1.4, yanchor="top"),
                margin=dict(t=10, r=90, b=90, l=90),
                xaxis=dict(
                    visible=True,
                    title="Time (s)",
                    range=[
                        0,
                        full_xvals[-1]
                        if full_xvals is not None
                        else len(self.measurement),
                    ],
                ),
                yaxis=dict(
                    title=f"Measurement ({crop_res.measurement.unit.replace('rad', 'degrees')})"
                ),
            ),
        )
        if len(crop_res.measurement) < len(full_res.measurement):
            fig.add_trace(
                go.Scatter(
                    x=full_xvals,
                    y=u(full_res.measurement.value),
                    name="Measurement",
                    mode="lines",
                    line=dict(color="blue", width=1, dash="dash"),
                    showlegend=showlegend
                )
            )
        
        fig.add_trace(
            go.Scatter(
                x=crop_xvals,
                y=u(crop_res.measurement.value),
                name="Selected" if len(crop_res.measurement) < len(full_res.measurement) else "Measurement",
                mode="lines",
                line=dict(color="blue", width=1, dash="solid"),
                showlegend=showlegend
            )
        )

        if len(dg.smoothers) > 1:
            fig.add_trace(
                go.Scatter(
                    x=crop_xvals,
                    y=u(crop_res.raw_sample),
                    name="Raw Sample",
                    mode="lines",
                    line=dict(color="black", width=1, dash="dash"),
                    showlegend=showlegend
                )
            )
        fig.add_trace(
            go.Scatter(
                x=crop_xvals,
                y=u(crop_res.sample),
                name="Smooth Sample" if len(dg.smoothers) > 1 else "Sample",
                mode="lines",
                line=dict(color="black", width=1, dash="solid"),
                showlegend=showlegend
            )
        )
        fig.add_trace(
            go.Scatter(
                x=crop_res.sample_keys[self.keys]
                if crop_xvals is None
                else crop_xvals[crop_res.keys],
                y=u(crop_res.sample[crop_res.keys]),
                text=np.round(crop_res.dgs, 3),
                hovertext=[crop_res.info(i) for i in range(len(crop_res.keys))],
                mode="markers",
                name="Downgrades",
                textposition=textposition,
                yaxis="y",
                marker=dict(size=10, color="black"),
                showlegend=showlegend
            )
        )
        fig.add_trace(
            go.Scatter(
                x=full_xvals,
                y=full_res.measurement.visibility,
                mode="lines",
                name="Visibility",
                yaxis="y2",
                line=dict(width=1, color="black", dash="dot"),
                showlegend=showlegend
            )
        )

        fig.add_vrect(
            x0=full_xvals[0],
            x1=crop_xvals[0],
            fillcolor="grey",
            opacity=0.2,
            line_width=0,
            showlegend=False
        )
        fig.add_vrect(
            x0=crop_xvals[-1],
            x1=full_xvals[-1],
            fillcolor="grey",
            opacity=0.2,
            line_width=0,
            showlegend=False
        )
        if crop_res.criteria.__class__.__name__ == "Bounded":
            fig.add_shape(
                type="rect",
                x0=crop_xvals[0],
                x1=crop_xvals[-1],
                y0=u(crop_res.criteria.max_bound)  if crop_res.criteria.max_bound is not None else -50,
                y1=u(crop_res.criteria.min_bound) if crop_res.criteria.min_bound is not None else 50,
                fillcolor="red",
                opacity=0.2,
                line_width=0,
                showlegend=False
            )

        return fig

    def results_subset_plot(self, names: list[str]):
        from plotly.subplots import make_subplots

        figs = [self.full_result_plot(name, i==0, "bottom left") for i, name in enumerate(names)]

        fig = make_subplots(
            rows=len(figs),
            cols=1,
            shared_xaxes=True,
            specs=[[{"secondary_y": True}] for _ in range(len(figs))],
            vertical_spacing=0.06,
        )

        for i, _fig in enumerate(figs, 1):
            for tr in _fig.data:
                fig.add_trace(tr, row=i, col=1, secondary_y=tr.name == "Visibility")
            for sh in _fig.layout.shapes:
                fig.add_shape(sh, row=i, col=1)

        axprops = dict(zerolinecolor="RGBA(0, 0, 0, 0.2)", zerolinewidth=2)

        axes = {}
        for i, _fig in enumerate(figs, 1):
            axes[f"xaxis{i if i > 1 else ''}"] = dict(
                visible=True, range=[0, self.fl.duration], **axprops
            ) | (dict(title="Time (s)") if i == len(figs) else {})
            axes[f"yaxis{2*i-1 if i>1 else ''}"] = dict(title=names[i-1], **axprops)
            axes[f"yaxis{2*i}"] = dict(title="Visibility", overlaying=f"y{2*i-1 if i>1 else ''}", range=[0, 1], side="right", **axprops)

        fig.update_layout(
            legend=dict(orientation="h", x=0, y=1 + 0.4 / len(figs), yanchor="top"),
            margin=dict(t=10, r=70, b=70, l=70),
            width=1000,
            height=250 * len(figs) + 50,
        )
        
        
        fig.update_layout(**axes)
        return fig

    def plot_results(self, name: str):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        result: Result = self.results[name]

        fig = make_subplots(
            1, 2,
            column_widths=[0.25, 0.75],
            specs=[[{"secondary_y": False,},{"secondary_y": True}]],
        )  # fmt: skip

        fig.add_trace(self.fl.pos.plotxz().data[0], row=1, col=1)

        fig.add_traces(
            [
                *result.measurement_trace(),
                *result.sample_trace(),
                result.downgrade_trace(),
            ],
            rows=1,
            cols=2,
        )
        fig.add_trace(
            result.visibility_trace(),
            row=1,
            col=2,
            secondary_y=True,
        )
        info = dict(
            **self.info(),
            **{"downgrade": result.total},
        )

        def format_float(v):
            return f"{v:.2f}" if isinstance(v, float) else v

        text = "<br>".join([f"{k}={format_float(v)}" for k, v in info.items()])

        fig.update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1),
            xaxis2=dict(range=[0, len(self.fl)]),
            height=300,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.0,
                xanchor="left",
                x=0.3,
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            # yaxis2=dict(range=[0, 2]),
            yaxis3=dict(range=[0, 1]),
            annotations=[
                go.layout.Annotation(
                    text=text,
                    align="left",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.2,
                    y=0.8,
                    bordercolor="black",
                    borderwidth=1,
                )
            ],
            scene=dict(
                aspectmode="data",
            ),
        )

        return fig

    def axisplot(self, camera: dict = None, **kwargs):
        import plotly.graph_objects as go

        fig: go.Figure = self.plot_3d(**kwargs)
        fig.update_layout(
            scene=dict(
                camera=dict(
                    eye=dict(x=0, y=-1, z=0),
                    projection=dict(type="orthographic"),
                )
                | (camera if camera is not None else {}),
            )
        )
        return fig
