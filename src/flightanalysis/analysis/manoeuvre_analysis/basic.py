from __future__ import annotations

from dataclasses import dataclass
import stat
from typing import Annotated
from xmlrpc.client import boolean

import numpy as np

import geometry as g
from flightdata import State
from schemas.positioning import Direction, Heading
from flightanalysis.definition import ManDef, ManOption
from schemas.sinfo import ScheduleInfo

from .analysis import Analysis
from schemas import MA, fcj
from importlib.metadata import version



@dataclass
class Basic(Analysis):
    id: int
    schedule_direction: Annotated[
        Heading | None, "The direction the schedule was flown in, None for inferred"
    ]
    flown: State
    mdef: ManDef | ManOption

    @property
    def name(self):
        return self.mdef.uid

    def __str__(self):
        res = f"{self.__class__.__name__}({self.id}, {self.mdef.info.short_name})"
        if isinstance(self, Scored):
            res = (
                res[:-1]
                + f", {', '.join([f'{k}={v:.2f}' for k, v in self.scores.score_summary(3, False).items()])})"
            )
        return res

    def __repr__(self):
        return str(self)

    def run_all(self, optimise_aligment=True, force=False) -> Scored:
        """Run the analysis to the final stage"""
        drs = [r._run(True) for r in self.run()]

        dr: Alignment = drs[np.argmin([dr[0] for dr in drs])][1]

        return dr.run_all(optimise_aligment, force)

    def proceed(self) -> Complete:
        """Proceed the analysis to the final stage for the case where the elements have already been labelled"""
        if "element" not in self.flown.labels.keys() or not isinstance(self, Basic):
            return self

        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef

        elnames = list(self.flown.labels.element.keys())
        for md in mopt:
            if len(elnames) != len(md.eds) or np.all([elnames[i] == k for i, k in enumerate(md.eds.data.keys())]):
                mdef = md
                break
        else:
            raise ValueError(
                f"{self.mdef.info.short_name} element sequence doesn't agree with {self.flown.data.element.unique()}"
            )

        itrans = self.create_itrans()
        man, tps = (
            mdef.create()
            .add_lines()
            .match_intention(State.from_transform(itrans), self.flown)
        )
        mdef = ManDef(mdef.info, mdef.mps.update_defaults(man), mdef.eds, mdef.box)
        return Complete(
            self.id,
            self.schedule_direction,
            self.flown,
            mdef,
            man,
            tps,
        )

    @staticmethod
    def from_dict(data: dict) -> Basic:
        return Basic(
            id=data["id"],
            schedule_direction=Heading[data["schedule_direction"]]
            if (data["schedule_direction"] and data["schedule_direction"] != "Infer")
            else None,
            flown=State.from_dict(data["flown"]),
            mdef=ManDef.from_dict(data["mdef"]),
        )

    def to_dict(self, basic: bool = False) -> dict:
        return dict(
            id=self.id,
            schedule_direction=self.schedule_direction.name
            if self.schedule_direction
            else None,
            flown=self.flown.to_dict(True),
            **(dict(mdef=self.mdef.to_dict()) if not basic else {}),
        )

    def create_itrans(self) -> g.Transformation:
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

    def run(self) -> list[Alignment]:
        itrans = self.create_itrans()
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef

        als = []
        for mdef in mopt:
            man = mdef.create().add_lines()
            als.append(
                Alignment(
                    self.id,
                    self.schedule_direction,
                    self.flown,
                    mdef,
                    man,
                    man.create_template(itrans),
                )
            )
        return als

    def export_ma(self, schedule: ScheduleInfo, history: dict = None) -> MA:
        return MA(
            **self.to_dict(),
            name=self.mdef.info.short_name,
            schedule=schedule,
            history={
                **(history if history else {}),
                **(
                    {
                        version("fatuning"): fcj.ManResult.model_validate(
                            self.fcj_results()
                        )
                    }
                    if self.__class__.__name__ == "Scored"
                    else {}
                ),
            },
        )

    @staticmethod
    def parse_analyse_serialise(pad: dict, optimise: boolean, name:str):
        import tuning
        from flightanalysis import enable_logging
        logger = enable_logging("INFO")
        logger.info(f"Running {name}")
        try:
            pad = Scored.from_dict(pad)
        except Exception as e:
            logger.exception(f"Failed to parse {pad['id']}")
            return pad
        
        try:
            pad = pad.proceed().run_all(optimise)
            logger.info(f"Completed {name}")
            return pad.to_dict()
        except Exception as e:
            logger.exception(f"Failed to process {name}")
            return pad.to_dict()

from .alignment import Alignment  # noqa: E402
from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402
