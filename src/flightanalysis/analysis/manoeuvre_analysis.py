from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Annotated, Self, Literal
from flightanalysis.definition import ManDef, ManOption
from flightanalysis.elements import AnyElement
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.analysis.el_analysis import ElementAnalysis
from flightanalysis.scoring.results import ElementsResults, ManoeuvreResults

from .aligment_optimisation import optimise_alignment
import numpy as np

import geometry as g
from flightdata import State, Alignment
from flightdata.state.alignment import AlignRadiusOption
from schemas.positioning import Direction, Heading


from loguru import logger


@dataclass
class Analysis:
    id: int
    schedule_direction: Annotated[
        Heading | None, "The direction the schedule was flown in, None for inferred"
    ]
    flown: State
    mdef: ManDef | ManOption
    itrans: g.Transformation | None = None
    manoeuvre: Manoeuvre | None = None
    templates: dict[str, State] | None = None
    scores: ManoeuvreResults | None = None

    @property
    def name(self):
        return self.mdef.info.short_name

    def run(
        self,
        optimise: bool = True,
        throw_errors: bool = False,
        stop_after: str = None,
        **kwargs,
    ) -> Self:
        stages = []
        if "element" in self.flown.labels.keys():
            stages.append("select_mdef")
        stages.append("create_itrans")
        if "element" not in self.flown.labels.keys():
            stages.extend(["preliminary_alignment", "secondary_alignment"])
        if optimise:
            stages.extend(["prepare_scoring", "optimise_alignment"])
        stages.extend(["prepare_scoring", "calculate_score"])

        for stage, fun in enumerate(stages):
            try:
                logger.debug(f"Running step {stage}: {fun}")
                self = getattr(self, fun)(**kwargs.get(fun, {}))
                if stop_after == fun:
                    logger.debug(f"Stopping after step {stage}: {fun}")
                    break
            except Exception as e:
                if throw_errors:
                    raise Exception(f"Error running {self.name}, {fun}: {e}") from e
                else:
                    logger.error(f"{self.name}, {fun}: {e}")
                    break

        return self

    def select_mdef(self):
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef

        elnames = list(self.flown.labels.element.keys())
        for md in mopt:
            if len(elnames) == len(md.eds) + 1 and np.all(
                [elnames[i] == k for i, k in enumerate(md.eds.data.keys())]
            ):
                mdef = md
                return replace(self, mdef=mdef)
        else:
            raise ValueError(
                f"{self.mdef.info.short_name} element sequence doesn't agree with {elnames}"
            )

    def _create_itrans(self) -> g.Transformation:
        if (
            self.schedule_direction
            and self.mdef.info.start.direction is not Direction.CROSS
        ):
            entry_direction = self.mdef.info.start.direction.wind_swap_heading(
                self.schedule_direction
            )
        else:
            entry_direction = Heading.infer(
                self.flown[0].att.transform_point(g.PX()).bearing()[0]
            )

        return g.Transformation(
            self.flown[0].pos,
            g.Euler(self.mdef.info.start.orientation.value, 0, entry_direction.value),
        )

    def create_itrans(self) -> g.Transformation:
        return replace(self, itrans=self._create_itrans())

    def _preliminary_alignment(
        self, mdef: ManDef, freq: int = 25, radius: AlignRadiusOption = 10
    ):
        manoeuvre = mdef.create().add_lines()
        templates = manoeuvre.create_template(self.itrans, None, freq, "min")
        template = State.stack(templates, "element")
        res = Alignment.align(self.flown, template, radius, True)

        return res.dist, res.aligned, manoeuvre, templates

    def preliminary_alignment(self, **kwargs) -> Self:
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef
        res = [self._preliminary_alignment(mdef, **kwargs) for mdef in mopt]
        option = np.argmin([r[0] for r in res])
        return replace(
            self,
            mdef=mopt[option],
            flown=res[option][1],
            manoeuvre=res[option][2],
            templates=res[option][3],
        )

    def secondary_alignment(self, freq: int = 25, radius: AlignRadiusOption = 10):
        manoeuvre, templates = self.manoeuvre.match_intention(
            self.itrans, self.flown, freq, "min", False
        )
        template = State.stack(templates, "element")
        res = Alignment.align(
            self.flown,
            template,
            radius,
            False,
        )

        return replace(
            self, flown=res.aligned, manoeuvre=manoeuvre, templates=templates
        )

    def prepare_scoring(self) -> Self:
        manoeuvre = (self.manoeuvre or self.mdef.create().add_lines()).match_intention(
            self.itrans, self.flown, 0, "min", True
        )[0]

        mdef = self.mdef.update_defaults(manoeuvre)
        corrected = mdef.create().add_lines()

        manoeuvre = manoeuvre.copy_directions(corrected)
        templates = manoeuvre.create_template(self.itrans, self.flown)

        return replace(self, mdef=mdef, manoeuvre=manoeuvre, templates=templates)

    def optimise_alignment(self):
        fl = optimise_alignment(self.flown, self.mdef, self.manoeuvre, self.templates)

        return replace(self, flown=fl)

    def intra(self, limits: bool = True):
        return ElementsResults([ea.intra_score(limits) for ea in self])

    def inter(self, limits: bool = True):
        return self.mdef.mps.collect(
            self.manoeuvre, self.flown, self.mdef.box, limits
        )

    def positioning(self, limits: bool = True):
        return self.mdef.box.score(self.mdef.info, self.flown, self.template)

    def calculate_score(self, limits: bool = True) -> Self:
        def fun(group: Literal["inter", "intra", "positioning"]):
            try:
                return getattr(self, group)(limits)
            except Exception as e:
                raise Exception(f"Error calculating {group} scores: {e}") from e

        return replace(
            self,
            scores=ManoeuvreResults(fun("inter"), fun("intra"), fun("positioning")),
        )

    def get_ea(self, name: str | int) -> ElementAnalysis:
        el: AnyElement = self.manoeuvre.elements[name]
        fl = self.flown.element[el.uid]
        tp = self.templates[el.uid].relocate(fl.pos[0])
        return ElementAnalysis(
            self.mdef.eds[name],
            self.mdef.mps,
            el,
            fl,
            tp,
            tp[0].transform,
            self.scores.intra[name] if self.scores else None,
        )

    def __getattr__(self, name: str):
        if name in self.flown.labels.element.keys():
            return self.get_ea(name)
        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")

    def __getitem__(self, name_or_id) -> ElementAnalysis:
        return self.get_ea(name_or_id)

    def __iter__(self):
        for edn in list(self.mdef.eds.data.keys()):
            yield self.get_ea(edn)

    def __str__(self):
        res = f"{self.__class__.__name__}({self.id}, {self.mdef.info.short_name})"
        if self.scores:
            res = (
                res[:-1]
                + f", {', '.join([f'{k}={v:.2f}' for k, v in self.scores.score_summary(3, False).items()])})"
            )
        return res

    def basic(self, mdef: ManDef = None, remove_labels: bool = False):
        return Analysis(
            id=self.id,
            schedule_direction=self.schedule_direction,
            flown=self.flown.remove_labels() if remove_labels else self.flown,
            mdef=mdef or self.mdef,
        )

    def move(self, transform: g.Transformation):
        return Analysis(
            self.id,
            self.schedule_direction,
            self.flown.move(transform),
            self.mdef,
            self.manoeuvre,
            {k: t.move(transform) for k, t in self.templates.items()}
            if self.templates
            else None,
        )

    @property
    def template(self):
        return State.stack(self.templates, "element") if self.templates else None

    @staticmethod
    def from_dict(data: dict):
        if "manoeuvre" in data and data["manoeuvre"]:
            manoeuvre = Manoeuvre.from_dict(data["manoeuvre"])
        else:
            manoeuvre = None

        if "templates" in data and data["templates"]:
            templates = {k: State.from_dict(v) for k, v in data["templates"].items()}
        else:
            templates = None

        itrans = list(templates.values())[0][0].transform if templates else None

        if "scores" in data and data["scores"]:
            scores = ManoeuvreResults.from_dict(data["scores"])
        else:
            scores = None

        return Analysis(
            data["id"],
            Heading[data["schedule_direction"]]
            if (data["schedule_direction"] and data["schedule_direction"] != "Infer")
            else None,
            State.from_dict(data["flown"]),
            ManDef.from_dict(data["mdef"]),
            itrans,
            manoeuvre,
            templates,
            scores,
        )

    def to_dict(self, basic: bool = False) -> dict:
        return dict(
            id=self.id,
            schedule_direction=self.schedule_direction.name
            if self.schedule_direction
            else None,
            flown=self.flown.to_dict(True),
            **(
                {}
                if basic
                else dict(
                    mdef=self.mdef.to_dict() if self.mdef else None,
                    manoeuvre=self.manoeuvre.to_dict() if self.manoeuvre else None,
                    templates={k: tp.to_dict(True) for k, tp in self.templates.items()}
                    if self.templates
                    else None,
                    scores=self.scores.to_dict() if self.scores else None,
                )
            ),
        )

    def fcj_results(self):
        return dict(
            els=[
                dict(name=k, start=v.start, stop=v.stop)
                for k, v in self.flown.labels.element.labels.items()
            ],
            results=self.scores.fcj_results(),
        )

    @staticmethod
    def parse_analyse_serialise(
        mad: dict, optimise: bool = False, throw_errors: bool = False, freq: int = 0
    ) -> dict:
        an = Analysis.from_dict(mad)
        return an.run(optimise, throw_errors, freq).to_dict()
