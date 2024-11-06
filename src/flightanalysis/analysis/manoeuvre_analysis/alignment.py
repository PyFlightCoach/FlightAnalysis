from __future__ import annotations

import traceback
from dataclasses import dataclass

from flightdata import State
from loguru import logger

from flightanalysis.definition import ManDef
from flightanalysis.elements import Element
from flightanalysis.manoeuvre import Manoeuvre

from ..el_analysis import ElementAnalysis
from .basic import Basic


@dataclass
class Alignment(Basic):
    manoeuvre: Manoeuvre | None
    template: State | None

    def __getattr__(self, name) -> ElementAnalysis:
        el: Element = self.manoeuvre.elements.data[name]
        return ElementAnalysis(
            self.mdef.eds.data[name],
            self.mdef.mps,
            el,
            el.get_data(self.flown),
            el.get_data(self.template),
            el.get_data(self.template)[0].transform,
        )

    def run_all(
        self, optimise_aligment=True, force=False
    ) -> Alignment | Complete | Scored:
        if self.__class__.__name__ == "Scored" and force:
            self = self.downgrade()
        new = self
        while self.__class__.__name__ != "Scored":
            try:
                new = (
                    self.run(optimise_aligment)
                    if isinstance(self, Complete)
                    else self.run()
                )
            except Exception:
                logger.error(traceback.format_exc())
            if new.__class__.__name__ == self.__class__.__name__:
                break
            self = new
        return new

    @staticmethod
    def from_dict(ajman: dict) -> Alignment | Basic:
        basic = Basic.from_dict(ajman)
        if isinstance(basic, Basic) and ajman["manoeuvre"] and ajman["template"]:
            return Alignment(
                **basic.__dict__,
                manoeuvre=Manoeuvre.from_dict(ajman["manoeuvre"]),
                template=State.from_dict(ajman["template"]),
            )
        else:
            return basic

    def to_dict(self, basic: bool=False) -> dict:
        _basic = super().to_dict(basic)
        if basic:
            return _basic
        return dict(
            **_basic,
            manoeuvre=self.manoeuvre.to_dict(),
            template=self.template.to_dict(),
        )

    def run(self) -> Alignment | Complete:
        if "element" not in self.flown.data.columns:
            try:
                self = self._run(True)[1]
            except Exception as e:
                logger.error(f"Failed to run alignment stage 1: {repr(e)}")
                return self
        try:
            return self._run(False)[1].proceed()
        except Exception as e:
            logger.error(f"Failed to run alignment stage 2: {repr(e)}")
            return self

    def _run(self, mirror=False, radius=10) -> Alignment:
        dist, aligned = State.align(self.flown, self.template, radius, mirror)
        return dist, self.update(aligned)

    def update(self, aligned: State) -> Alignment:
        man, tp = self.manoeuvre.match_intention(self.template[0], aligned)
        mdef = ManDef(
            self.mdef.info,
            self.mdef.mps.update_defaults(man),
            self.mdef.eds,
            self.mdef.box,
        )
        return Alignment(self.id, self.schedule_direction, aligned, mdef, man, tp)

    def _proceed(self) -> Complete:
        if "element" in self.flown.data.columns:
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

    def fcj_results(self):
        df = self.flown.label_ranges("element").iloc[:, :3]
        df.columns = ["name", "start", "stop"]
        return dict(els=df.to_dict("records"))


from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402
