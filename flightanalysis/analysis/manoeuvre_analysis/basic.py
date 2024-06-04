from __future__ import annotations
from dataclasses import dataclass
from flightdata import State, Flight, Origin
from flightanalysis.definition import ManDef, SchedDef, ManOption
import geometry as g
from json import load
from .analysis import AlinmentStage, Analysis
from flightanalysis.definition.scheduleinfo import ScheduleInfo
import numpy as np
import pandas as pd


@dataclass
class Basic(Analysis):
    mdef: ManDef | ManOption
    flown: State
    direction: int
    stage: AlinmentStage

    @property
    def name(self):
        return self.mdef.uid

    def run_all(self, optimise_aligment=True):
        """Run the analysis to the final stage, for the case where the elements have not been labelled"""
        res = [s.run_all(False) for s in self.run(False)]
        self = res[0]
        if len(res) > 1:
            for r in res[1:]:
                if r.stage < self.stage:
                    continue
                if r.dist < self.dist:
                    self = r

        if isinstance(self, Scored) and optimise_aligment:
            self = Complete(**{k:v for k, v in list(self.__dict__.items())[:-1]}).run(True)
            self.stage = AlinmentStage.SECONDARY
            self = self.run_all(True)
                   
        return self

    def proceed(self, optimise_alignment=False) -> Scored:
        """Proceed the analysis to the final stage for the case where the elements have already been labelled"""
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef
        elnames = self.flown.data.element.unique()
        for md in mopt:
            if np.all(elnames[1:-1] == list( md.eds.data.keys())):
                mdef = md
                break
        else:
            raise ValueError(f"{self.mdef.info.short_name} element sequence doesn't agree with {self.flown.data.element.unique()}")

        itrans = self.create_itrans()
        man, tp = mdef.create(itrans).add_lines().match_intention(
            State.from_transform(itrans),
            self.flown
        )
        mdef = ManDef(mdef.info, mdef.mps.update_defaults(man), mdef.eds)
        corr = mdef.create(itrans).add_lines()
        return Complete(
            mdef, self.flown, self.direction, AlinmentStage.SECONDARY,
            1e9, man, tp, corr, corr.create_template(itrans, self.flown)
        ).run(optimise_alignment)

    @classmethod
    def from_dict(Cls, data:dict) -> Basic:
        return Basic(
            ManDef.from_dict(data["mdef"]),
            State.from_dict(data["flown"]),
            data['direction'],
            data['stage']
        )

    def create_itrans(self) -> g.Transformation:
        return g.Transformation( 
            self.flown[0].pos, 
            self.mdef.info.start.initial_rotation(self.direction)
        )

    @staticmethod
    def from_fcj(file: str, mid: int):
        with open(file, 'r') as f:
            data = load(f)
        flight = Flight.from_fc_json(data)
        box = Origin.from_fcjson_parmameters(data["parameters"])

        sdef = SchedDef.load(data["parameters"]["schedule"][1])

        state = State.from_flight(flight, box).splitter_labels(
            data["mans"],
            [m.info.short_name for m in sdef]
        )
        mdef= sdef[mid]
        return Basic(mdef, state.get_manoeuvre(mdef.uid), AlinmentStage.SETUP)

    def run(self, optimise_aligment=True) -> list[Alignment]:
        itrans = self.create_itrans()
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef

        als = []        
        for mdef in mopt:
            man = mdef.create(itrans).add_lines()
            als.append(Alignment(
                mdef, self.flown, self.direction, AlinmentStage.SETUP, 
                1e9, man, man.create_template(itrans)
            ))
        return als

    def to_mindict(self, sinfo: ScheduleInfo):
        return dict(
            **super().to_mindict(sinfo),
            manoeuvre=self.name,
            data=self.flown._create_json_data().to_dict('records'),
            direction=self.direction,
        ) 

    @staticmethod
    def from_mindict(data: dict):
        mdef = getattr(SchedDef.load(ScheduleInfo(**data['sinfo'])), data['manoeuvre'])
        st = State.from_flight(Flight.from_fc_json(data))
        
        if 'els' in data:
            df = pd.DataFrame(data['els'])
            df.columns = ['name', 'start', 'stop', 'length']
            st = st.splitter_labels(df.to_dict('records'), target_col='element').label(manoeuvre=data['manoeuvre'])

        return Basic(mdef, st, data['direction'], AlinmentStage.SETUP)
    

from .alignment import Alignment  # noqa: E402
from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402