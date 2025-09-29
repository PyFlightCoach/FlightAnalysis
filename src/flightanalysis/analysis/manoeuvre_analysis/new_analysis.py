from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Annotated, Self
from flightanalysis.definition import ManDef, ManOption, ElDef
from flightanalysis.elements import AnyElement, Elements
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.analysis.el_analysis import ElementAnalysis
from flightanalysis.scoring.results import ElementsResults, Results, ManoeuvreResults
import numpy as np

import geometry as g
from flightdata import State, align
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
        return self.mdef.uid

    def run(self, optimise: bool = True):
        for stage, fun in enumerate(
            [self.create_itrans]
            + (
                [
                    self.select_mdef,
                    self.create_itrans,
                ]
                if "element" in self.flown.labels.keys()
                else [
                    self.preliminary_alignment,
                    self.secondary_alignment,
                ]
            )
            + [
                self.prepare_scoring,
                lambda: self.optimise_alignment() if optimise else self,
                self.prepare_scoring,
                self.calculate_score,
            ]
        ):
            try:
                logger.info(f"Running step {stage}: {fun.__name__}")
                self = fun(self)
            except Exception as e:
                logger.error(f"Error in {fun.__name__}: {e}")
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
        return replace(self, itrans=self.create_itrans())

    def _preliminary_alignment(self, mdef: ManDef):
        manoeuvre = mdef.create().add_lines()
        templates = manoeuvre.create_template(self.itrans, None, 0, "min")
        template = State.stack(templates, "element")
        res = align(self.flown, template, len(self.flown) and len(template), True)

        return res.dist, res.aligned, manoeuvre, templates

    def preliminary_alignment(self) -> Self:
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef
        res = [self._preliminary_alignment(mdef) for mdef in mopt]
        option = np.argmin([r[0] for r in res])
        return self.replace(
            mdef=mopt[option],
            flown=res[option][1],
            manoeuvre=res[option][2],
            templates=res[option][3],
        )

    def secondary_alignment(self):
        manoeuvre, templates = self.manoeuvre.match_intention(
            self.create_itrans(), self.flown, 0, "min", False
        )
        template = State.stack(templates, "element")
        res = align(
            template,
            self.flown,
            len(self.flown) and len(template),
            False,
        )

        return replace(
            self, flown=res.aligned, manoeuvre=manoeuvre, templates=templates
        )

    def prepare_scoring(self) -> Self:
        manoeuvre = (self.manoeuvre or self.mdef.create().add_lines()).match_intention(
            self.itrans, None, 0, "min", True
        )[0]

        mdef = self.mdef.update_defaults(manoeuvre)
        corrected = mdef.create().add_lines()

        manoeuvre = manoeuvre.copy_directions(corrected)
        templates = manoeuvre.create_template(self.itrans, self.flown)

        return replace(self, mdef=mdef, manoeuvre=manoeuvre, templates=templates)

    def _get_score(
        self, eln: str, itrans: g.Transformation, fl: State
    ) -> tuple[Results, g.Transformation]:
        ed: ElDef = self.get_edef(eln)
        el: AnyElement = self.manoeuvre.all_elements()[eln].match_intention(itrans, fl)
        tp = el.create_template(State.from_transform(itrans), fl)

        return ed.dgs.apply(el, fl, tp, False), el, tp  # tp[-1].att

    def _optimise_split(
        self,
        itrans: g.Transformation,
        eln1: str,
        eln2: str,
        fl: State,
        min_len: int = 3,
    ) -> int:
        el1: AnyElement = self.manoeuvre.all_elements()[eln1]
        el2: AnyElement = self.manoeuvre.all_elements()[eln2]

        def score_split(steps: int) -> float:
            new_fl = fl.step_label("element", eln1, steps, fl.t, min_len)
            res1, oel1, tp1 = self._get_score(eln1, itrans, el1.get_data(new_fl))

            el2fl = el2.get_data(new_fl)
            res2, oel2, tp2 = self._get_score(
                eln2, g.Transformation(tp1[-1].att, el2fl[0].pos), el2fl
            )

            oman = Manoeuvre.from_all_elements(
                self.manoeuvre.uid,
                Elements(self.manoeuvre.elements.data | {eln1: oel1, eln2: oel2}),
            )

            omdef = self.mdef.update_defaults(oman)

            inter = omdef.mps.collect(
                oman,
                State.stack(self.templates | {eln1: tp1, eln2: tp2}, "element"),
                self.mdef.box,
            )

            logger.debug(f"split {steps} {res1.total + res2.total:.2f}")
            logger.debug(
                f"e1={eln1}, e2={eln2}, steps={steps}, intra={res1.total + res2.total:.2f}, inter={inter.total}"
            )
            return res1.total + res2.total + inter.total

        dgs = {0: score_split(0)}

        def check_steps(stps: int):
            new_l2 = len(el2.get_data(fl)) - stps + 1
            new_l1 = len(el1.get_data(fl)) + stps + 1
            return new_l2 > min_len and new_l1 > min_len

        steps = int(len(el1.get_data(fl)) > len(el2.get_data(fl))) * 2 - 1

        if not check_steps(steps):
            return 0

        try:
            new_dg = score_split(steps)
            if new_dg > dgs[0]:
                steps = -steps
            else:
                dgs[steps] = new_dg
                steps += np.sign(steps)
        except Exception:
            steps = -steps

        while check_steps(steps):
            try:
                new_dg = score_split(steps)
                if new_dg < list(dgs.values())[-1]:
                    dgs[steps] = new_dg
                    steps += np.sign(steps)
                else:
                    break
            except ValueError:
                break

        min_dg_step = np.argmin(np.array(list(dgs.values())))
        out_steps = list(dgs.keys())[min_dg_step]
        return out_steps

    def optimise_alignment(self):
        fl = self.flown.copy()
        elns = list(self.mdef.eds.data.keys())

        padjusted = set(elns)
        count = 0
        while len(padjusted) > 0 and count < 2:
            adjusted = set()
            for eln1, eln2 in zip(elns[:-1], elns[1:]):
                if (eln1 in padjusted) or (eln2 in padjusted):
                    itrans = g.Transformation(
                        self.templates[eln1][0].att,
                        self.flown.element[eln1][0].pos,
                    )
                    steps = self._optimise_split(itrans, eln1, eln2, fl)

                    if not steps == 0:
                        logger.debug(
                            f"Adjusting split between {eln1} and {eln2} by {steps} steps"
                        )
                        fl = fl.step_label("element", eln1, steps, fl.t, 3)
                        adjusted.update([eln1, eln2])

            padjusted = adjusted
            count += 1
            logger.debug(
                f"pass {count}, {len(padjusted)} elements adjusted:\n{padjusted}"
            )

        return Analysis(
            self.id,
            self.schedule_direction,
            fl,
            self.mdef,
        )

    def intra(self, limits: bool = True):
        return ElementsResults([ea.intra_score(limits) for ea in self])

    def inter(self, limits: bool = True):
        return self.mdef.mps.collect(
            self.manoeuvre, self.template, self.mdef.box, limits
        )

    def positioning(self, limits: bool = True):
        return self.mdef.box.score(self.mdef.info, self.flown, self.template)

    def calculate_score(self, limits: bool = True) -> Self:
        return replace(
            self,
            scores=ManoeuvreResults(
                self.inter(limits), self.intra(limits), self.positioning(limits)
            ),
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

        if templates:
            itrans = list(templates.values())[0][0].transform
        else:
            itrans = None

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
            **({} if basic else dict(
                mdef=self.mdef.to_dict() if self.mdef else None,
                manoeuvre=self.manoeuvre.to_dict() if self.manoeuvre else None,
                templates={k: tp.to_dict(True) for k, tp in self.templates.items()} if self.templates else None,
                scores=self.scores.to_dict() if self.scores else None,
            )),
        )
    
    def fcj_results(self):
        return dict(
            els=[
                dict(name=k, start=v.start, stop=v.stop)
                for k, v in self.flown.labels.element.labels.items()
            ],
            results=self.scores.fcj_results(),
        )