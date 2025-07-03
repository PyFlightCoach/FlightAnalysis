from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from numbers import Number

from flightanalysis.elements.element import Elements
import geometry as g
import numpy as np
import pandas as pd
from flightdata import State
from loguru import logger
from joblib import Parallel, delayed

from flightanalysis.definition import ElDef, ManDef
from flightanalysis.elements import Element
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.scoring import (
    ElementsResults,
    ManoeuvreResults,
    Results,
)
import os

from ..el_analysis import ElementAnalysis
from .alignment import Alignment
from .basic import Basic


@dataclass(repr=False)
class Complete(Alignment):
    # corrected: Manoeuvre
    # corrected_templates: dict[str, State]

    @staticmethod
    def from_dict(ajman: dict) -> Complete | Alignment | Basic:
        return Alignment.from_dict(ajman).proceed()

    def to_dict(self, basic: bool = False) -> dict:
        return super().to_dict(basic)

    def run(self, optimise_aligment=True) -> Scored:
        if optimise_aligment:
            self = self.optimise_alignment()
        self = self.update_templates()
        return Scored(
            **self.__dict__,
            scores=ManoeuvreResults(self.inter(), self.intra(), self.positioning()),
        )

    def update_templates(self):
        if not len(self.flown) == len(self.template) or not np.all(
            self.flown.element == self.template.element
        ):
            manoeuvre, template = self.manoeuvre.match_intention(
                self.template[0], self.flown
            )

            return Complete(
                self.id,
                self.schedule_direction,
                self.flown,
                self.mdef.update_defaults(manoeuvre),
                manoeuvre,
                template,
            )
        else:
            return self

    def get_score(
        self, eln: str, itrans: g.Transformation, fl: State
    ) -> tuple[Results, g.Transformation]:
        ed: ElDef = self.get_edef(eln)
        el: Element = self.manoeuvre.all_elements()[eln].match_intention(itrans, fl)
        tp = el.create_template(State.from_transform(itrans), fl)

        #        full_tp = State.stack(self.templates | {eln: tp})

        return ed.dgs.apply(el, fl, tp, False), el, tp  # tp[-1].att

    def optimise_split(
        self, itrans: g.Transformation, eln1: str, eln2: str, fl: State, min_len: int = 3
    ) -> int:
        el1: Element = self.manoeuvre.all_elements()[eln1]
        el2: Element = self.manoeuvre.all_elements()[eln2]

        def score_split(steps: int) -> float:
            new_fl = fl.step_label("element", eln1, steps, fl.t, min_len)
            res1, oel1, tp1 = self.get_score(eln1, itrans, el1.get_data(new_fl))

            el2fl = el2.get_data(new_fl)
            res2, oel2, tp2 = self.get_score(
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
#            return not (
#                (stps > 0 and len(el2.get_data(fl)) <= stps + min_len)
#                or (stps < 0 and len(el1.get_data(fl)) <= -stps + min_len)
#            )

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

                        # fl = fl.shift_label(steps, 2, manoeuvre=self.name, element=eln1)
                        fl = fl.step_label("element", eln1, steps, fl.t, 3)
                        adjusted.update([eln1, eln2])

            padjusted = adjusted
            count += 1
            logger.debug(
                f"pass {count}, {len(padjusted)} elements adjusted:\n{padjusted}"
            )

        return Basic(self.id, self.schedule_direction, fl, self.mdef).proceed()

    def optimise_alignment_v2(self):
        pass

    def intra(self):
        return ElementsResults([ea.intra_score() for ea in self])

    def inter(self):
        return self.mdef.mps.collect(self.manoeuvre, self.template, self.mdef.box)

    def positioning(self):
        return self.mdef.box.score(self.mdef.info, self.flown, self.template)

    def plot_3d(self, **kwargs):
        from plotting import plotsec

        fig = self.flown.plotlabels("element")
        return plotsec(self.flown, color="blue", nmodels=20, fig=fig, **kwargs)

    def set_boundaries(self, boundaries: list[float]):
        new_man = Basic(
            self.id,
            self.schedule_direction,
            self.flown.set_boundaries("element", boundaries),  # .resample(),
            self.mdef,
        ).proceed()

        return new_man.run_all(False) if isinstance(self, Scored) else new_man

    def set_boundary(self, el: str | int, boundary: float):
        # TODO check if boundary is within bounds
        boundaries = self.flown.labels.element.boundaries
        elid = el if isinstance(el, int) else self.elnames.index(el)
        boundaries[elid] = boundary
        return self.set_boundaries(boundaries)

    def boundary_sweep(self, el: str | int, width: float, substeps: int = 5):
        """Sweep an element boundary through a width and return a set of results
        width is in seconds,
        substeps is the number of steps to take within each timestep
        TODO make sure range doesn't cross adjacent boundary
        """
        elid = el if isinstance(el, int) else self.elnames.index(el)
        bopt = self.flown.labels.element.boundaries[elid]
        tstart = bopt - width
        tstop = bopt + width
        ts = self.flown.data.t[tstart:tstop].to_numpy()
        splits = np.array(
            [
                t0 + (t1 - t0) * i / substeps
                for t0, t1 in zip(ts[:-1], ts[1:])
                for i in range(substeps)
            ]
        )
        logger.info(
            f"Starting {os.cpu_count() * 2 - 1} processes to run {len(splits)} manoeuvres"
        )
        madicts = Parallel(n_jobs=os.cpu_count() * 2 - 1)(
            delayed(partial(Basic.parse_analyse_serialise, optimise=False, name=i))(
                self.set_boundary(el, ic).to_dict()
            )
            for i, ic in enumerate(splits)
        )
        outdata = {
            ic: Scored.from_dict(mad).scores.dg_dict()
            for ic, mad in zip(splits, madicts)
        }

        return pd.DataFrame(outdata).T


from .scored import Scored  # noqa: E402
