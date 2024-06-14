from dataclasses import dataclass
from flightanalysis.data import list_resources


fcj_categories = {
    'F3A FAI':'f3a',
    'F3A':'f3a',
    'US AMA':'nsrca',
    'F3A UK':'f3auk',
    'F3A US':'nsrca',
    'IMAC':'imac',
}

fcj_schedules = {
    'P23': 'p23',
    'F23': 'f23',
    'P25': 'p25',
    'F25': 'f25',
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

    def fcj_to_pfc(self):
        def lookup(val, data):
            return data[val] if val in data else val

        return ScheduleInfo(
            lookup(self.category, fcj_categories),
            lookup(self.name, fcj_schedules)
        )

    def pfc_to_fcj(self):

        def rev_lookup(val, data):
            return next(k for k, v in data.items() if v == val) if val in data.values() else val

        return ScheduleInfo(
            rev_lookup(self.category, fcj_categories),
            rev_lookup(self.name, fcj_schedules)
        )

    @staticmethod
    def from_fcj_sch(sch):
        return ScheduleInfo(*sch).fcj_to_pfc()

    def to_fcj_sch(self):
        return list(self.pfc_to_fcj().__dict__.values())

    @staticmethod
    def build(category, name):
        return ScheduleInfo(category.lower(), name.lower())


schedule_library = [ScheduleInfo.from_str(fname) for fname in list_resources('schedule')]
