from . import ManDef, ManInfo, ManOption, ScheduleInfo
from flightdata import State
from typing import Tuple, Union, Self
from geometry import Transformation
from flightanalysis.schedule import Schedule
from flightanalysis.elements import Line
from flightdata import Collection
from json import dump, load
from flightdata import NumpyEncoder
from flightanalysis.data import get_json_resource


class SchedDef(Collection):
    VType=ManDef
    def __init__(self, data: dict[str, VType] | list[VType] = None):
        super().__init__(data, check_types=False)
        assert all([v.__class__.__name__ in ['ManOption', 'ManDef'] for v in self])

    def add_new_manoeuvre(self, info: ManInfo, defaults=None):
        return self.add(ManDef(info,defaults))

    def create_template(self,depth:float=170, wind:int=-1) -> Tuple[Schedule, State]:
        templates = []
        ipos = self[0].info.initial_position(depth,wind)
        
        mans = []
        for md in self:
            md = md[md.active] if isinstance(md, ManOption) else md
                
            itrans=Transformation(
                ipos if len(templates) == 0 else templates[-1][-1].pos,
                md.info.start.initial_rotation(wind) if len(templates) == 0 else templates[-1][-1].att
            )
            man = md.create(itrans)
            templates.append(man.create_template(itrans))
            mans.append(man)
        return Schedule(mans), State.stack(templates)

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
        from flightplotting import plotdtw
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
            kind.lower()
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