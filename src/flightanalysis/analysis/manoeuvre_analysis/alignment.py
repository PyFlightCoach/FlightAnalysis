from __future__ import annotations

import traceback
from dataclasses import dataclass

from flightdata import State, align
from loguru import logger

from flightanalysis.definition import ManDef
from flightanalysis.elements import Element
from flightanalysis.manoeuvre import Manoeuvre

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

        return ElementAnalysis(
            self.mdef.eds[name_or_id],
            self.mdef.mps,
            el,
            self.flown.element[el.uid],
            self.templates[el.uid],
            self.templates[el.uid][0].transform,
        )

    def __getattr__(self, name) -> ElementAnalysis:
        return self.get_ea(name)

    def __getitem__(self, name_or_id) -> ElementAnalysis:
        return self.get_ea(name_or_id)

    def run_all(
        self, optimise_aligment=True, force=False
    ) -> Alignment | Complete | Scored:
        if self.__class__.__name__ == "Scored" and force:
            self = self.downgrade()
        while self.__class__.__name__ != "Scored":
            #try:
            self = (
                self.run(optimise_aligment)
                if isinstance(self, Complete)
                else self.run()
            )
            #except Exception as ex:
            #    logger.error(traceback.format_exc())
            #    if throw:
            #        raise Exception(f"Alignment error, {self.name}") from ex
        return self

    @staticmethod
    def from_dict(ajman: dict) -> Alignment | Basic:
        basic = Basic.from_dict(ajman)
        if isinstance(basic, Basic) and ajman["manoeuvre"]:
            if "template" in ajman:
                if set(ajman["template"].keys()) == set(
                    [el["uid"] for el in ajman["manoeuvre"]["elements"]] + ["exit_line"]
                ):
                    return Alignment(
                        **basic.__dict__,
                        manoeuvre=Manoeuvre.from_dict(ajman["manoeuvre"]),
                        templates={
                            k: State.from_dict(v) for k, v in ajman["template"].items()
                        }
                        if "templates" in ajman
                        else None,
                    )
        return basic

    def to_dict(self, basic: bool = False) -> dict:
        _basic = super().to_dict(basic)
        if basic:
            return _basic
        return dict(
            **_basic,
            manoeuvre=self.manoeuvre.to_dict(),
            template={k: tp.to_dict() for k, tp in self.templates.items()},
        )

    def run(self) -> Alignment | Complete:
        if "element" not in self.flown.labels.lgs:
            #try:
                return self._run(True)[1]
            #except Exception as e:
            #    logger.error(f"Failed to run alignment stage 1: {repr(e)}")
            #    return self
        #try:
        return self._run(False)[1].proceed()
        #except Exception as e:
        #    logger.error(f"Failed to run alignment stage 2: {repr(e)}")
        #    return self

    def _run(self, mirror=False, radius=10) -> Alignment:
        res = align(self.flown, self.template, radius, mirror)
        return res.dist, self.update(res.aligned)

    def update(self, aligned: State) -> Alignment:
        man, tps = self.manoeuvre.match_intention(self.template_list[0][0], aligned)
        mdef = ManDef(
            self.mdef.info,
            self.mdef.mps.update_defaults(man),
            self.mdef.eds,
            self.mdef.box,
        )
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

    def fcj_results(self):
        return self.flown.labels.element.to_iloc(self.flown.t).to_dict()


#        df = self.flown.label_ranges("element").iloc[:, :3]
#        df.columns = ["name", "start", "stop"]
#        return dict(els=df.to_dict("records"))


from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402
