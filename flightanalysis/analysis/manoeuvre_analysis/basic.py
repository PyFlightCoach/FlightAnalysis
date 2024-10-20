from __future__ import annotations

from dataclasses import dataclass
from json import load
from typing import Annotated

import geometry as g
import numpy as np
import pandas as pd
from flightdata import Flight, Origin, State

from flightanalysis.definition import ManDef, ManOption, SchedDef, Direction
from flightanalysis.definition.maninfo import Heading
from flightanalysis.definition.scheduleinfo import ScheduleInfo

from .analysis import Analysis


@dataclass
class Basic(Analysis):
    id: int
    schedule: ScheduleInfo
    schedule_direction: Annotated[
        Heading | None, "The direction the schedule was flown in in, None for inferred"
    ]
    flown: State
    mdef: ManDef | ManOption

    @property
    def name(self):
        return self.mdef.uid

    def run_all(self, optimise_aligment=True, force=False) -> Scored:
        """Run the analysis to the final stage"""
        drs = [r._run(True) for r in self.run()]

        dr = drs[np.argmin([dr[0] for dr in drs])]

        return dr[1].run_all(optimise_aligment, force)

    def proceed(self) -> Complete:
        """Proceed the analysis to the final stage for the case where the elements have already been labelled"""
        if (
            "element" not in self.flown.data.columns
            or self.flown.data.element.isna().any()
            or not isinstance(self, Basic)
        ):
            return self

        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef
        elnames = self.flown.data.element.unique().astype(str)
        for md in mopt:
            if np.all(
                [np.any(np.char.startswith(elnames, k)) for k in md.eds.data.keys()]
            ):
                mdef = md
                break
        else:
            raise ValueError(
                f"{self.mdef.info.short_name} element sequence doesn't agree with {self.flown.data.element.unique()}"
            )

        itrans = self.create_itrans()
        man, tp = (
            mdef.create()
            .add_lines()
            .match_intention(State.from_transform(itrans), self.flown)
        )
        mdef = ManDef(mdef.info, mdef.mps.update_defaults(man), mdef.eds, mdef.box)
        corr = mdef.create().add_lines()
        return Complete(
            self.id,
            self.schedule,
            self.schedule_direction,
            self.flown,
            mdef,
            man,
            tp,
            corr,
            corr.create_template(itrans, self.flown),
        )

    @staticmethod
    def from_dict(data: dict) -> Basic:
        return Basic(
            id=data["id"],
            schedule=data["schedule"],
            schedule_direction=Heading[data["schedule_direction"]]
            if (data["schedule_direction"] and data['schedule_direction'] != "Infer")
            else None,
            flown=State.from_dict(data["flown"]),
            mdef=ManDef.from_dict(data["mdef"])
            if data["mdef"]
            else ManDef.load(data["schedule"], data["name"]),
        )

    def to_dict(self, basic:bool=False) -> dict:
        return dict(
            id=self.id,
            schedule=self.schedule.__dict__,
            schedule_direction=self.schedule_direction.name if self.schedule_direction else None,
            flown=self.flown.to_dict(),
            **(dict(mdef=self.mdef.to_dict()) if not basic else {}),
        )

    def create_itrans(self) -> g.Transformation:
        if self.schedule_direction and self.mdef.info.start.direction is not Direction.CROSS:
            entry_direction = self.mdef.info.start.direction.wind_swap_heading(self.schedule_direction)
        else:
            entry_direction = Heading.infer(self.flown[0].att.transform_point(g.PX()).bearing()[0])

        return g.Transformation(
            self.flown[0].pos,
            g.Euler(self.mdef.info.start.orientation.value, 0, entry_direction.value),
        )

    @staticmethod
    def from_fcj(file: str, mid: int):
        with open(file, "r") as f:
            data = load(f)

        flight = Flight.from_fc_json(data)
        box = Origin.from_fcjson_parameters(data["parameters"])

        sinfo = ScheduleInfo.build(**data["parameters"]["schedule"]).fcj_to_pfc()
        

        state: State = State.from_flight(flight[
            data['data'][data['mans'][mid]['start']]['time'],
            data['data'][data['mans'][mid]['stop']]['time']
        ], box)

        mdef = ManDef.load(sinfo, mid)

        schedule_direction = (
            Heading.infer(state[data['data'][data['mans'][1]['start']]['time']].bearing()[0])
        )

        return Basic(mid, sinfo, schedule_direction, mdef, state)

    def run(self) -> list[Alignment]:
        itrans = self.create_itrans()
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef

        als = []
        for mdef in mopt:
            man = mdef.create().add_lines()
            als.append(
                Alignment(
                    self.id,
                    self.schedule,
                    self.schedule_direction,
                    self.flown,
                    mdef,
                    man,
                    man.create_template(itrans),
                )
            )
        return als


from .alignment import Alignment  # noqa: E402
from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402
