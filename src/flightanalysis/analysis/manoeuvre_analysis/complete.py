from __future__ import annotations

from dataclasses import dataclass

import geometry as g
import numpy as np
from flightdata import State
from loguru import logger

from flightanalysis.definition import ElDef, ManDef
from flightanalysis.elements import Element
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.scoring import (
    ElementsResults,
    ManoeuvreResults,
    Results,
)

from ..el_analysis import ElementAnalysis
from .alignment import Alignment
from .basic import Basic


@dataclass
class Complete(Alignment):
    corrected: Manoeuvre
    corrected_template: State

    @staticmethod
    def from_dict(ajman: dict) -> Complete | Alignment | Basic:
        analysis = Alignment.from_dict(ajman)
        if (
            isinstance(analysis, Alignment)
            and ajman["corrected"]
            and ajman["corrected_template"]
        ):
            return Complete(
                **analysis.__dict__,
                corrected=Manoeuvre.from_dict(ajman["corrected"]),
                corrected_template=State.from_dict(ajman["corrected_template"]),
            )
        else:
            return analysis

    def to_dict(self, basic: bool=False) -> dict:
        _basic = super().to_dict(basic)
        if basic:
            return _basic
        return dict(
            **_basic,
            corrected=self.corrected.to_dict(),
            corrected_template=self.corrected_template.to_dict(),
        )

    def run(self, optimise_aligment=True) -> Scored:
        if optimise_aligment:
            self = self.optimise_alignment()
        self = self.update_templates()
        return Scored(
            **self.__dict__,
            scores=ManoeuvreResults(self.inter(), self.intra(), self.positioning()),
        )

    @property
    def elnames(self):
        return list(self.mdef.eds.data.keys())

    def __iter__(self):
        for edn in list(self.mdef.eds.data.keys()):
            yield self.get_ea(edn)

    def __getitem__(self, i):
        return self.get_ea(self.mdef.eds[i + 1].name)

    def __getattr__(self, name):
        if name in self.mdef.eds.data.keys():
            return self.get_ea(name)
        raise AttributeError(f"Attribute {name} not found in {self.__class__.__name__}")

    def get_edef(self, name):
        return self.mdef.eds[name]

    def get_ea(self, name):
        el: Element = getattr(self.manoeuvre.all_elements(), name)
        st = el.get_data(self.flown)
        tp = el.get_data(self.template).relocate(st.pos[0])

        return ElementAnalysis(
            self.get_edef(name), self.mdef.mps, el, st, tp, el.ref_frame(tp)
        )

    def update_templates(self):
        if not len(self.flown) == len(self.template) or not np.all(
            self.flown.element == self.template.element
        ):
            manoeuvre, template = self.manoeuvre.match_intention(
                self.template[0], self.flown
            )
            mdef = ManDef(
                self.mdef.info,
                self.mdef.mps.update_defaults(self.manoeuvre),
                self.mdef.eds,
            )
            correction = mdef.create().add_lines()

            return Complete(
                self.id,
                self.schedule_direction,
                self.flown,
                mdef,
                manoeuvre,
                template,
                correction,
                correction.create_template(template[0], self.flown),
            )
        else:
            return self

    def get_score(
        self, eln: str, itrans: g.Transformation, fl: State
    ) -> tuple[Results, g.Transformation]:
        ed: ElDef = self.get_edef(eln)
        el: Element = self.manoeuvre.all_elements()[eln].match_intention(itrans, fl)
        tp = el.create_template(State.from_transform(itrans), fl)
        return ed.dgs.apply(el, fl, tp, False), tp[-1].att

    def optimise_split(
        self, itrans: g.Transformation, eln1: str, eln2: str, fl: State
    ) -> int:
        el1: Element = self.manoeuvre.all_elements()[eln1]
        el2: Element = self.manoeuvre.all_elements()[eln2]

        def score_split(steps: int) -> float:
            new_fl = fl.shift_label(steps, 2, manoeuvre=self.name, element=eln1)
            res1, new_iatt = self.get_score(eln1, itrans, el1.get_data(new_fl))

            el2fl = el2.get_data(new_fl)
            res2 = self.get_score(
                eln2, g.Transformation(new_iatt, el2fl[0].pos), el2fl
            )[0]
            logger.debug(f"split {steps} {res1.total + res2.total:.2f}")
            logger.debug(
                f"e1={eln1}, e2={eln2}, steps={steps}, dg={res1.total + res2.total:.2f}"
            )
            return res1.total + res2.total

        dgs = {0: score_split(0)}

        steps = int(len(el1.get_data(fl)) > len(el2.get_data(fl))) * 2 - 1

        new_dg = score_split(steps)
        if new_dg > dgs[0]:
            steps = -steps
        else:
            steps += np.sign(steps)
            dgs[steps] = new_dg

        while True:
            if (steps > 0 and len(el2.get_data(fl)) <= steps + 3) or (
                steps < 0 and len(el1.get_data(fl)) <= -steps + 3
            ):
                break
            new_dg = score_split(steps)

            if new_dg < list(dgs.values())[-1]:
                dgs[steps] = new_dg
                steps += np.sign(steps)
            else:
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
                        self.manoeuvre.all_elements()[eln1]
                        .get_data(self.template)[0]
                        .att,
                        self.manoeuvre.all_elements()[eln1].get_data(fl)[0].pos,
                    )
                    steps = self.optimise_split(itrans, eln1, eln2, fl)

                    if not steps == 0:
                        logger.debug(
                            f"Adjusting split between {eln1} and {eln2} by {steps} steps"
                        )

                        fl = fl.shift_label(steps, 2, manoeuvre=self.name, element=eln1)

                        adjusted.update([eln1, eln2])

            padjusted = adjusted
            count += 1
            logger.debug(
                f"pass {count}, {len(padjusted)} elements adjusted:\n{padjusted}"
            )

        return Basic(self.id, self.schedule_direction, fl, self.mdef).proceed()

    def intra(self):
        return ElementsResults([ea.intra_score() for ea in self])

    def inter(self):
        return self.mdef.mps.collect(self.manoeuvre, self.template, self.mdef.box)

    def positioning(self):
        return self.mdef.box.score(self.mdef.info, self.flown, self.template)

    def plot_3d(self, **kwargs):
        from plotting import plotdtw, plotsec

        fig = plotdtw(self.flown, self.flown.data.element.unique())
        return plotsec(self.flown, color="blue", nmodels=20, fig=fig, **kwargs)


from .scored import Scored  # noqa: E402
