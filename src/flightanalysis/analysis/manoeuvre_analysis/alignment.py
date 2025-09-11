from __future__ import annotations

from dataclasses import dataclass
from loguru import logger
import geometry as g
from schemas.positioning import Direction, Heading

from flightdata import State, align

from flightanalysis.elements import Element
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.definition.mandef import ManDef

from ..el_analysis import ElementAnalysis
from .basic import Basic


@dataclass(repr=False)
class Alignment(Basic):
    manoeuvre: Manoeuvre | None
    templates: dict[str, State] | None

    @property
    def template(self):
        return State.stack(self.templates, "element")

    @property
    def template_list(self):
        return list(self.templates.values())

    def get_ea(self, name_or_id: str | int) -> ElementAnalysis:
        el: Element = self.manoeuvre.elements[name_or_id]
        fl = self.flown.element[el.uid]
        tp = self.templates[el.uid].relocate(fl.pos[0])
        return ElementAnalysis(
            self.mdef.eds[name_or_id],
            self.mdef.mps,
            el,
            fl,
            tp,
            tp[0].transform,
            self.scores.intra[name_or_id] if isinstance(self, Scored) else None,
        )

    def __getattr__(self, name) -> ElementAnalysis:
        return self.get_ea(name)

    def __getitem__(self, name_or_id) -> ElementAnalysis:
        return self.get_ea(name_or_id)

    def __iter__(self):
        for edn in list(self.mdef.eds.data.keys()):
            yield self.get_ea(edn)

    def run_all(
        self, optimise_aligment=True, force=False, throw_errors=True
    ) -> Alignment | Complete | Scored:
        if self.__class__.__name__ == "Scored" and force:
            self = self.downgrade()
        try:
            while self.__class__.__name__ != "Scored":
                self = (
                    self.run(optimise_aligment)
                    if isinstance(self, Complete)
                    else self.run()
                )
        except Exception as ex:
            if throw_errors:
                raise ex
            logger.exception(f"Error in run_all at {self.__class__.__name__}: {ex}")
        return self

    @staticmethod
    def from_dict(ajman: dict) -> Alignment | Basic:
        basic = Basic.from_dict(ajman)
        if isinstance(basic, Basic) and "manoeuvre" in ajman and ajman["manoeuvre"]:
            manoeuvre = Manoeuvre.from_dict(ajman["manoeuvre"])

            trust_templates = (
                "templates" in ajman
                and ajman["templates"] is not None
                and set(ajman["templates"].keys())
                == set(
                    [el["uid"] for el in ajman["manoeuvre"]["elements"]] + ["exit_line"]
                )
            )

            return Alignment(
                **basic.__dict__,
                manoeuvre=manoeuvre,
                templates={k: State.from_dict(v) for k, v in ajman["templates"].items()}
                if trust_templates
                else manoeuvre.create_template(basic.create_itrans(), basic.flown),
            )
        return basic

    def to_dict(self, basic: bool = False) -> dict:
        _basic = super().to_dict(basic)
        if basic:
            return _basic
        return dict(
            **_basic,
            manoeuvre=self.manoeuvre.to_dict(),
            templates={k: tp.to_dict(True) for k, tp in self.templates.items()},
        )

    def update_templates(self):
        if (
            not len(self.flown) == len(self.template)
            or not self.flown.labels.element.keys()
            == self.template.labels.element.keys()
        ):
            manoeuvre, template = self.manoeuvre.match_intention(
                self.template[0], self.flown
            )
        else:
            manoeuvre, template = self.manoeuvre, self.template

        corrected = self.mdef.create().add_lines()
        manoeuvre = manoeuvre.copy_directions(corrected)

        Obj = Complete if self.__class__ is Scored else self.__class__
            
        return Obj(
            self.id,
            self.schedule_direction,
            self.flown,
            self.mdef,
            manoeuvre,
            manoeuvre.create_template(template[0], self.flown),
        )

    def proceed(self) -> Alignment | Complete:
        if "element" in self.flown.labels.lgs:
            return Complete(
                self.id,
                self.schedule_direction,
                self.flown,
                self.mdef,
                self.manoeuvre,
                self.templates,
            ).update_templates()
        else:
            return self

    def run(self) -> Alignment | Complete:
        if "element" not in self.flown.labels.lgs:
            return self._run(True)[1]
        self = self._run(False)[1]

        return self.proceed()

    def _run(self, mirror=False, radius=10) -> Alignment:
        res = align(self.flown, self.template, radius, mirror)
        return res.dist, self.update(res.aligned)

    @staticmethod
    def build(
        id: int, schedule_direction: Heading, flown: State, mdef: ManDef
    ) -> Alignment:
        itrans = Basic(id, schedule_direction, flown, mdef).create_itrans()
        manoeuvre = mdef.create().add_lines()
        return Alignment(
            id,
            schedule_direction,
            flown,
            mdef,
            manoeuvre,
            manoeuvre.create_template(itrans, flown),
        )

    def update(self, aligned: State) -> Alignment:
        man, tps = self.manoeuvre.match_intention(self.create_itrans(), aligned)
        mdef = self.mdef.update_defaults(man)
        return Alignment(self.id, self.schedule_direction, aligned, mdef, man, tps)

    def _proceed(self) -> Complete:
        if "element" in self.flown.labels.keys():
            correction = self.mdef.create()
            return Complete(
                self.id,
                self.schedule_direction,
                self.flown,
                self.mdef,
                self.manoeuvre,
                self.template,
                correction,
                correction.create_template(self.template[0], self.flown),
            )
        else:
            return self

    def move(self, trans: g.Transformation):
        return Alignment(
            self.id,
            self.schedule_direction,
            self.flown.move(trans),
            self.mdef,
            self.manoeuvre,
            {k: t.move(trans) for k, t in self.templates.items()},
        )

    def plot_element(
        self,
        eln: str,
        long_name: str,
        camera: dict = None,
        jpannotation: dict = None,
        elannotation: dict = None,
        fig=None,
    ):
        import plotly.graph_objects as go
        from plotting import plotsec

        ea: ElementAnalysis = self.get_ea(eln)

        colors = [
            "blue" if el.uid == ea.el.uid else "grey" for el in self.manoeuvre.elements
        ]

        fig: go.Figure = plotsec(
            {k: fl for k, fl in self.flown.element.items()},
            color=colors,
            scale=10,
            tips=False,
            ribb=True,
            nmodels=0,
        )
        fig = g.P0().plot3d(mode="markers", fig=fig, marker=dict(size=5, color="black"))

        fig = self.flown.plot(
            fig=fig, ribb=False, nmodels=2, color="grey", scale=10, tips=False
        )
        fig = ea.fl.plot(
            fig=fig, ribb=False, nmodels=2, color="red", scale=10, tips=False
        )

        xrng = [
            min(self.flown.data.x.min() - 20, 0),
            max(self.flown.data.x.max() + 20, 0),
        ]
        yrng = [0, self.flown.data.y.max() + 20]
        zrng = [0, self.flown.data.z.max() + 20]

        arx = xrng[1] - xrng[0]
        ary = yrng[1] - yrng[0]
        arz = zrng[1] - zrng[0]

        mrng = max(arx, ary, arz)
        arx = arx / mrng
        ary = ary / mrng
        arz = arz / mrng

        ec = ea.fl.pos[len(ea.fl.pos) // 2]

        fig.update_layout(
            font=dict(family="Rockwell", size=14),
            scene=dict(
                aspectmode="manual",
                camera=dict(
                    eye=dict(x=-1.1, y=-1.1, z=0.4),
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0.1, z=-0.2),
                )
                | camera
                if camera is not None
                else {},
                xaxis=dict(range=xrng, title_font_size=16, title="x (m)"),
                yaxis=dict(range=yrng, title_font_size=16, title="y (m)"),
                zaxis=dict(range=zrng, title_font_size=16, title="z (m)"),
                aspectratio=dict(x=arx, y=ary, z=arz),
                annotations=[
                    dict(
                        x=0,
                        y=0,
                        z=0,
                        text="Judge Position",
                        showarrow=True,
                        font=dict(size=16),
                        # arrowcolor="black",
                        arrowhead=2,
                        arrowsize=2,
                        arrowwidth=1,
                    )
                    | ({} if jpannotation is None else jpannotation),
                    dict(
                        x=ec.x[0],
                        y=ec.y[0],
                        z=ec.z[0],
                        text=long_name,
                        showarrow=True,
                        font=dict(size=16),
                        # arrowcolor="black",
                        arrowhead=2,
                        arrowsize=2,
                        arrowwidth=1,
                    )
                    | ({} if elannotation is None else elannotation),
                ],
            ),
            width=600,
            height=500,
        )
        return fig


from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402
