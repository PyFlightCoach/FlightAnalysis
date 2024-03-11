from . import ManDef, ManInfo, ManParms
from flightdata import State
from typing import Dict, Tuple, Union, Self
from geometry import Transformation
from flightanalysis.schedule import Schedule
from flightanalysis.elements import Line
from flightdata import Collection, State
from json import dump, load
from flightdata.base.numpy_encoder import NumpyEncoder
from dataclasses import dataclass
from flightanalysis.data import list_resources, get_json_resource
from json import dump


fcj_schedule_names = {
    'f3a': ['F3A', 'F3A FAI'],
    'nsrca': ['F3A US'],
    'f3auk': ['F3A UK'],
    'imac': ['IMAC']
}

@dataclass
class ScheduleInfo:
    category: str
    name: str

    @staticmethod
    def from_str(fname):
        if fname.endswith("_schedule.json"):
            fname = fname[:-14]
        info = fname.split("_")
        if len(info) == 1:
            return ScheduleInfo("f3a", info[0].lower())
        else:
            return ScheduleInfo(info[0].lower(), info[1].lower())

    def __str__(self):
        return f"{self.category}_{self.name}".lower()

    def definition(self):
        return SchedDef.load(self)

    @staticmethod
    def from_fcj_sch(fcj):
        for k, v in fcj_schedule_names.items():
            if fcj[0] in v:
                return ScheduleInfo(k, fcj[1])
        raise ValueError(f"Unknown schedule {fcj}")    

    def to_fcj_sch(self):
        return [fcj_schedule_names[self.category][-1], self.name]

    @staticmethod
    def build(category, name):
        return ScheduleInfo(category.lower(), name.lower())


schedule_library = [ScheduleInfo.from_str(fname) for fname in list_resources('schedule')]


class SchedDef(Collection):
    VType=ManDef
    def add_new_manoeuvre(self, info: ManInfo, defaults=None):
        return self.add(ManDef(info,defaults))

    def create_schedule(self, depth: float, wind: float) -> Schedule:
        return Schedule(
            {m.uid: m.create(m.info.initial_transform(depth, wind)) for m in self}
        )      

    def create_template(self,depth:float=170, wind:int=-1) -> Tuple[Schedule, State]:
        templates = []
        ipos = self[0].info.initial_position(depth,wind)
        
        mans = []
        for md in self:

            itrans=Transformation(
                ipos if len(templates) == 0 else templates[-1][-1].pos,
                md.info.start.initial_rotation(wind) if len(templates) == 0 else templates[-1][-1].att
            )
            man = md.create(itrans)
            templates.append(man.create_template(itrans))
            mans.append(man)
        return Schedule(mans), State.stack(templates)

    def create_el_matched_template(self, intended: Schedule):
        for md, man in zip(self, intended):
            if isinstance(man, Line):
                pass

    def update_defaults(self, sched: Schedule):
        # TODO need to consider the entry line
        for md, man in zip(self, sched):
            md.mps.update_defaults(man)

    def to_json(self, file: str) -> str:
        with open(file, "w") as f:
            dump(self.to_dict(), f, cls=NumpyEncoder, indent=2)
        return file

    @staticmethod
    def from_json(file:str):
        with open(file, "r") as f:
            return SchedDef.from_dict(load(f))
        
    @staticmethod
    def load(name: Union[str,ScheduleInfo]) -> Self:
        sinfo = ScheduleInfo.from_str(name) if isinstance(name, str) else name 
            
        return SchedDef.from_dict(get_json_resource(f"{str(sinfo).lower()}_schedule"))
    

    def plot(self):
        sched, template = self.create_template(170, 1)
        from flightplotting import plotsec, plotdtw
        return plotdtw(template, template.data.manoeuvre.unique())

    def label_exit_lines(self, sti: State):
        mans = list(self.data.keys()) + ['landing']
        
        meids = [sti.data.columns.get_loc(l) for l in ['manoeuvre', 'element']]
        
        sts = [sti.get_manoeuvre(0)]
        
        for mo, m in zip(mans[:-1], mans[1:]):
            st = sti.get_manoeuvre(m)
            #if not 'exit_line' in sts[-1].element:
            entry_len = st.get_label_len(element='entry_line')
            
            st.data.iloc[:int(entry_len/2), meids] = [mo, 'exit_line']
            sts.append(st)
        
        sts[0].data.iloc[
            :int(sts[0].get_label_len(element='entry_line')/2), 
            meids
        ] = ['tkoff', 'exit_line']
        
        return State.stack(sts, 0)

    def create_fcj(self, sname: str, path: str, wind=1, scale=1, kind='f3a'):
        sched, template = self.create_template(170, 1)
        template = State.stack([
            template, 
            Line(30, 100, uid='entry_line').create_template(template[-1]).label(manoeuvre='landing')
        ])
        
        if not scale == 1:
            template = template.scale(scale)
        if wind == -1:
            template=template.mirror_zy()

        fcj = self.label_exit_lines(template).create_fc_json(
            [0] + [man.info.k for man in self] + [0],
            sname,
            fcj_schedule_names[kind.lower()][-1]
        )
            
        with open(path, 'w') as f:
            dump(fcj, f)

    def create_fcjs(self, sname, folder, kind='F3A'):
        winds = [-1, -1, 1, 1]
        distances = [170, 150, 170, 150]
        
        for wind, distance in zip(winds, distances):
            w = 'A' if wind == 1 else 'B'
            fname = f'{folder}/{sname}_template_{distance}_{w}.json'
            print(fname)
            self.create_fcj(
                sname, 
                fname, 
                wind, distance/170,
                kind
            )