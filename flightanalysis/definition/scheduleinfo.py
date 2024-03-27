from dataclasses import dataclass
from flightanalysis.data import list_resources


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
