from __future__ import annotations
from dataclasses import dataclass
from flightdata import State, Flight, Origin
from flightanalysis.definition import ManDef, SchedDef, ManOption
from flightanalysis.definition.maninfo import Heading
import geometry as g
from json import load
from .analysis import Analysis
from flightanalysis.definition.scheduleinfo import ScheduleInfo
import numpy as np
import pandas as pd
from typing import Annotated


@dataclass
class Basic(Analysis):
    mdef: ManDef | ManOption
    flown: State
    entry: Annotated[Heading | None, "The direction the manoeuvre should start in, None for inferred"]
    exit: Annotated[Heading | None, "The direction the manoeuvre should end in, None for inferred"]

    @property
    def name(self):
        return self.mdef.uid


    def to_analysis_dict(self) -> dict:
        return dict(
            id=self.id,
            mdef=self.mdef.to_dict(),
            flown=self.flown.to_dict(),
            entry=self.entry.name if self.entry else None,
            exit=self.exit.name if self.exit else None,
        )

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
            mdef,
            self.flown,
            self.entry,
            self.exit,
            man,
            tp,
            corr,
            corr.create_template(itrans, self.flown),
        )

    def to_dict(self) -> dict:
        return dict(
            mdef=self.mdef.to_dict(),
            flown=self.flown.to_dict(),
            entry=self.entry.name if self.entry else None,
            exit=self.exit.name if self.exit else None,
        )

    @classmethod
    def from_dict(Cls, data: dict) -> Basic:
        return Basic(
            -1,
            ManDef.from_dict(data["mdef"]),
            State.from_dict(data["flown"]),
            Heading[data["entry"]] if data["entry"] else None,
            Heading[data["exit"]] if data["exit"] else None,
        )

    def create_itrans(self) -> g.Transformation:
        entry = (
            self.entry
            if self.entry is not None
            else Heading.infer(self.flown[0].att.transform_point(g.PX()).bearing()[0])
        )

        return g.Transformation(
            self.flown[0].pos,
            g.Euler(self.mdef.info.start.orientation.value, 0, entry.value),
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
                    mdef,
                    self.flown,
                    self.entry,
                    self.exit,
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
            entry=self.entry.name,
            exit=self.exit.name,
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
