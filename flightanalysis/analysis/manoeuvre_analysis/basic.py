from __future__ import annotations

from dataclasses import dataclass
from json import load
from typing import Annotated

import geometry as g
import numpy as np
import pandas as pd
from flightdata import Flight, Origin, State

from flightanalysis.definition import ManDef, ManOption, SchedDef
from flightanalysis.definition.maninfo import Heading
from flightanalysis.definition.scheduleinfo import ScheduleInfo

from .analysis import Analysis


@dataclass
class Basic(Analysis):
    id: int
    schedule: ScheduleInfo
    flown: State
    mdef: ManDef | ManOption
    entryDirection: Annotated[
        Heading | None, "The direction the manoeuvre should start in, None for inferred"
    ]
    exitDirection: Annotated[
        Heading | None, "The direction the manoeuvre should end in, None for inferred"
    ]

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
            self.flown,
            mdef,
            self.entryDirection,
            self.exitDirection,
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
            flown=State.from_dict(data["flown"]),
            mdef=ManDef.from_dict(data["mdef"])
            if data["mdef"]
            else ManDef.load(data["schedule"], data["name"]),
            entryDirection=Heading.parse(data["entryDirection"])
            if data["entryDirection"]
            else None,
            exitDirection=Heading.parse(data["entryDirection"])
            if data["entryDirection"]
            else None,
        )

    def to_dict(self, basic:bool=False) -> dict:
        return dict(
            id=self.id,
            schedule=self.schedule.__dict__,
            flown=self.flown.to_dict(),
            **(dict(mdef=self.mdef.to_dict()) if not basic else {}),
            entryDirection=self.entryDirection.name if self.entryDirection else None,
            exitDirection=self.exitDirection.name if self.exitDirection else None,
        )

    def create_itrans(self) -> g.Transformation:
        entryDirection = (
            self.entryDirection
            if self.entryDirection is not None
            else Heading.infer(self.flown[0].att.transform_point(g.PX()).bearing()[0])
        )

        return g.Transformation(
            self.flown[0].pos,
            g.Euler(self.mdef.info.start.orientation.value, 0, entryDirection.value),
        )

    @staticmethod
    def from_fcj(file: str, mid: int):
        with open(file, "r") as f:
            data = load(f)
        flight = Flight.from_fc_json(data)
        box = Origin.from_fcjson_parameters(data["parameters"])

        sdef = SchedDef.load(data["parameters"]["schedule"][1])

        state = State.from_flight(flight, box).splitter_labels(
            data["mans"], [m.info.short_name for m in sdef]
        )
        mdef = sdef[mid]
        return Basic(mid, mdef, state.get_manoeuvre(mdef.uid))

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
                    self.flown,
                    mdef,
                    self.entryDirection,
                    self.exitDirection,
                    man,
                    man.create_template(itrans),
                )
            )
        return als

    def to_mindict(self, sinfo: ScheduleInfo):
        data = dict(
            **super().to_mindict(sinfo),
            name=self.name,
            id=self.id,
            data=self.flown._create_json_data().to_dict("records"),
            entryDirection=self.entryDirection.name,
            exitDirection=self.exitDirection.name,
        )
        return data

    @staticmethod
    def from_mindict(data: dict):
        info = ScheduleInfo.from_str(data["parameters"]["schedule"][1])

        st = State.from_flight(
            Flight.from_fc_json(data),
            Origin.from_fcjson_parmameters(data["parameters"]),
        )

        mdef = SchedDef.load(info)[data["id"]]

        if "els" in data:
            df = pd.DataFrame(data["els"])
            df.columns = ["name", "start", "stop", "length"]
            st = st.splitter_labels(df.to_dict("records"), target_col="element").label(
                manoeuvre=data["name"]
            )

        return Basic(data["id"], mdef, st, data["direction"])


from .alignment import Alignment  # noqa: E402
from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402
