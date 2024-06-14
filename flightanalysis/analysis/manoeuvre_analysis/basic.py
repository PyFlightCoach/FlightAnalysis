from __future__ import annotations
from dataclasses import dataclass
from flightdata import State, Flight, Origin
from flightanalysis.definition import ManDef, SchedDef, ManOption
import geometry as g
from json import load
from .analysis import Analysis
from flightanalysis.definition.scheduleinfo import ScheduleInfo
import numpy as np
import pandas as pd


@dataclass
class Basic(Analysis):
    mdef: ManDef | ManOption
    flown: State
    direction: int

    @property
    def name(self):
        return self.mdef.uid

    def run_all(self, optimise_aligment=True, force=False) -> Scored:
        """Run the analysis to the final stage, for the case where the elements have not been labelled"""
        drs = [r._run(True) for r in self.run()]
        
        dr = drs[np.argmin([dr[0] for dr in drs])]

        return dr[1].run_all(optimise_aligment, force)

    def proceed(self) -> Complete:
        """Proceed the analysis to the final stage for the case where the elements have already been labelled"""
        if 'element' not in self.flown.data.columns:
            return self
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
            self.id, mdef, self.flown, self.direction,
            man, tp, corr, corr.create_template(itrans, self.flown)
        )

    @classmethod
    def from_dict(Cls, data:dict) -> Basic:
        return Basic(
            -1,
            ManDef.from_dict(data["mdef"]),
            State.from_dict(data["flown"]),
            data['direction']
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
        return Basic(mid, mdef, state.get_manoeuvre(mdef.uid))

    def run(self) -> list[Alignment]:
        itrans = self.create_itrans()
        mopt = ManOption([self.mdef]) if isinstance(self.mdef, ManDef) else self.mdef

        als = []        
        for mdef in mopt:
            man = mdef.create(itrans).add_lines()
            als.append(Alignment(
                self.id, mdef, self.flown, self.direction, 
                man, man.create_template(itrans)
            ))
        return als

    def to_mindict(self, sinfo: ScheduleInfo):
        data = dict(
            **super().to_mindict(sinfo),
            name=self.name,
            id=self.id,
            data=self.flown._create_json_data().to_dict('records'),
            direction=self.direction,
        ) 
        return data

    @staticmethod
    def from_mindict(data: dict):
        info = ScheduleInfo.from_str(data["parameters"]["schedule"][1])
        
        st = State.from_flight(
            Flight.from_fc_json(data), 
            Origin.from_fcjson_parmameters(data["parameters"])
        )
        
        mdef = SchedDef.load(info)[data['id']] 
        
        if 'els' in data:
            df = pd.DataFrame(data['els'])
            df.columns = ['name', 'start', 'stop', 'length']
            st = st.splitter_labels(df.to_dict('records'), target_col='element').label(manoeuvre=data['name'])

        return Basic(data['id'], mdef, st, data['direction'])
    

from .alignment import Alignment  # noqa: E402
from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402