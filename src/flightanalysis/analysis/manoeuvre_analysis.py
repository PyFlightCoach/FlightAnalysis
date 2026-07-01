from __future__ import annotations

from dataclasses import dataclass, replace
from json import dumps
from typing import Annotated, Self, Literal
from flightanalysis.definition import ManDef, ManOption
from flightanalysis.elements import AnyElement
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.analysis.el_analysis import ElementAnalysis
from flightanalysis.scoring.results import ElementsResults, ManoeuvreResults
import numpy as np

import geometry as g
from flightdata import State, Alignment
from flightdata.state.alignment import AlignRadiusOption
from schemas.positioning import Direction, Heading
from schemas import MA

from loguru import logger


class ElSequenceError(Exception):
    pass


@dataclass
class Analysis:
    id: int
    schedule_direction: Annotated[
        Heading | None, "The direction the schedule was flown in, None for inferred"
    ]
    flown: State
    mdef: ManDef | ManOption
    option: int | None = None
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
        force: bool = True,
        **kwargs,
    ) -> Self:
        if self.scores and not force:
            logger.info(f"Analysis {self.id} already has scores, skipping run.")
            return self
        stages = [
            ("create_itrans", True),
            ("select_mdef", "element" in self.flown.labels.keys()),
            ("preliminary_alignment", "element" not in self.flown.labels.keys()),
            ("secondary_alignment", "element" not in self.flown.labels.keys()),
            ("prepare_scoring", optimise),
            ("optimise_alignment", optimise),
            ("prepare_scoring", True),
            ("calculate_score", True),
        ]
        for stage, (fun_name, run) in enumerate(stages):
            if run:
                try:
                    logger.debug(f"Running step {stage}: {fun_name}")
                    self = getattr(self, fun_name)(**kwargs.get(fun_name, {}))
                    if stop_after == fun_name:
                        logger.debug(f"Stopping after step {stage}: {fun_name}")
                        break
                except ElSequenceError as ese:
                    if throw_errors:
                        raise ElSequenceError(
                            f"Error running {self.name}, {fun_name}: {ese}"
                        ) from ese
                    else:
                        logger.warning(f"{self.name}, {fun_name}: {ese}")
                        stages[2] = (stages[2][0], True)
                        stages[3] = (stages[3][0], True)
                except Exception as e:
                    if throw_errors:
                        raise Exception(
                            f"Error running {self.name}, {fun_name}: {e}"
                        ) from e
                    else:
                        logger.error(f"{self.name}, {fun_name}: {e}")
                        break
            else:
                logger.debug(f"Skipping step {stage}: {fun_name}")
        return self

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

    def select_mdef(self):
        """If the elements are labelled it should be possible to select the correct option.
        First find all the options that match the element sequence.
        If more than one option matches, select the one with the best score.

        There is a problem if both options have the same element names
        in this case we need to score both and choose the best.

        NOTE (0.5.1 on) - added option index to the class, so if that exists use that.
        If not then do the old check and set the option for next time.
        This function can be simplified once all the old analyses have been updated with the option.
        """
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef

        elnames = list(self.flown.labels.element.keys())

        options = []
        for md in mopt:
            if len(elnames) == len(md.eds) and np.all(
                [elnames[i] == k for i, k in enumerate(md.eds.data.keys())]
            ):
                options.append(md)
        if len(options) == 0:
            raise ElSequenceError(
                f"{self.mdef.info.short_name} element sequence doesn't agree with {elnames}"
            )
        elif self.option is not None:
            option_id = self.option
        elif len(options) == 1:
            option_id = 0
        else:
            scores = []
            for option in options:
                scores.append(replace(self, mdef=option).run(False).scores.score())
            option_id = np.argmax(scores)
        return replace(self, mdef=options[option_id], option=option_id)

    def _preliminary_alignment(
        self, mdef: ManDef, freq: int = 25, radius: AlignRadiusOption = 10
    ):
        manoeuvre = mdef.create()
        templates = manoeuvre.create_template(self.itrans, None, freq, "min")
        template = State.stack(templates, "element")
        res = Alignment.align(self.flown, template, radius, True)

        return res.dist, res.aligned, manoeuvre, templates

    def preliminary_alignment(self, **kwargs) -> Self:
        """Run DTW alignment for each option, select the one with the lowest distance.
        TODO this is not proving very reliable for the P27 top hat."""
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
        manoeuvre = (self.manoeuvre or self.mdef.create()).match_intention(
            self.itrans, self.flown, 0, "min", True
        )[0]

        mdef = self.mdef.update_defaults(manoeuvre)
        corrected = mdef.create()

        manoeuvre = manoeuvre.copy_directions(corrected)
        templates = manoeuvre.create_template(self.itrans, self.flown)

        return replace(self, mdef=mdef, manoeuvre=manoeuvre, templates=templates)

    def optimise_alignment(self, include_inter: bool = True) -> Self:
        steps = {}
        for el in list(self.manoeuvre.elements.keys())[:-1]:
            for step_size in [5, 1]:
                steps[el], self = self.optimise_boundary(el, include_inter, step_size)
        logger.debug(f"optimisation result:\n{dumps(steps, indent=2)}")
        return self

    def intra(self):
        return ElementsResults([ea.intra_score() for ea in self])

    def inter(self):
        return self.mdef.mps.collect(self.manoeuvre, self.flown, self.mdef.box)

    def positioning(self):
        return self.mdef.box.score(
            self.mdef.info, self.manoeuvre.elements, self.flown, self.template
        )

    def calculate_score(self) -> Self:
        def fun(group: Literal["inter", "intra", "positioning"]):
            try:
                return getattr(self, group)()
            except Exception as e:
                raise Exception(f"Error calculating {group} scores: {e}") from e

        return replace(
            self,
            scores=ManoeuvreResults(fun("inter"), fun("intra"), fun("positioning")),
        )

    def reload_element(self, name: str | int) -> Self:
        ist = self.templates[name][0].relocate(self.flown.element[name][0].pos)
        new_man = self.manoeuvre.replace_elements(
            **{
                name: self.manoeuvre.elements[name].match_intention(
                    ist, self.flown.element[name]
                )
            }
        )
        new_templates = self.templates | {
            name: new_man.elements[name].create_template(ist, self.flown.element[name])
        }

        return replace(
            self,
            mdef=replace(self.mdef, mps=self.mdef.mps.update_defaults(new_man)),
            manoeuvre=new_man,
            templates=new_templates,
            scores=None,
        )

    def update_boundaries(self, new_fl: State) -> Self:
        changes = [
            k
            for k in self.manoeuvre.elements.keys()
            if new_fl.labels.element[k] != self.flown.labels.element[k]
        ]
        _new: Self = replace(self, flown=new_fl)
        for change in changes:
            _new = _new.reload_element(change)
        return _new

    def shift_boundary(self, boundary: str, t: float) -> Self:
        return self.update_boundaries(
            self.flown.move_label(
                "element", boundary, self.flown.labels.element[boundary].stop + t
            )
        )

    def step_boundary(self, boundary: str, steps: int) -> Self:
        return self.update_boundaries(
            self.flown.step_label("element", boundary, steps, self.flown.t, 3)
        )

    def score_boundary(self, boundary: str, include_inter: bool = True):
        next_el = self.manoeuvre.elnames[self.manoeuvre.elnames.index(boundary) + 1]
        return ElementsResults(
            {
                boundary: self[boundary].intra_score(),
                next_el: self[next_el].intra_score(),
                **({"inter": self.inter()} if include_inter else {}),
            }
        )

    def optimise_boundary(
        self, boundary: str, include_inter: bool = True, step_size: int = 1
    ) -> list[Self | int]:
        next_el = self.manoeuvre.elnames[self.manoeuvre.elnames.index(boundary) + 1]

        def score_step(_steps: int):
            try:
                _new = self.step_boundary(boundary, _steps)
                _results = _new.score_boundary(boundary, include_inter)
                return [_results.total, _new]
            except Exception as _:
                return None

        best = score_step(0)
        direction = (
            -1
            if self.flown.labels.element[boundary].width
            > self.flown.labels.element[next_el].width
            else 1
        )

        _check = score_step(direction * step_size)
        if _check is not None and _check[0] < best[0]:
            best = _check
            steps = direction * step_size
        else:
            direction = -direction
            steps = 0

        while True:
            steps += direction * step_size
            _check = score_step(steps)
            if _check is not None and _check[0] < best[0]:
                best = _check
            else:
                return steps, best[1]

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

    def __getattr__(self, name: str) -> ElementAnalysis:
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
            self.itrans,
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
        manoeuvre = (
            Manoeuvre.from_dict(data["manoeuvre"]) if data.get("manoeuvre") else None
        )

        templates = (
            {k: State.from_dict(v) for k, v in data["templates"].items()}
            if data.get("templates")
            else None
        )

        itrans = list(templates.values())[0][0].transform if templates else None

        scores = (
            ManoeuvreResults.from_dict(data["scores"]) if data.get("scores") else None
        )

        return Analysis(
            data["id"],
            Heading[data["schedule_direction"]]
            if (data["schedule_direction"] and data["schedule_direction"] != "Infer")
            else None,
            State.from_dict(data["flown"]),
            ManDef.from_dict(data["mdef"]),
            data.get("option"),
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
            option=self.option,
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

    def update_ma(self, ma: MA, long: bool = False) -> MA:
        return ma.model_copy(
            update=self.to_dict(basic=not long)
        )

    @staticmethod
    def parse_analyse_serialise(
        mad: dict, optimise: bool = False, throw_errors: bool = False, freq: int = 0
    ) -> dict:
        an = Analysis.from_dict(mad)
        return an.run(optimise, throw_errors, freq).to_dict()
