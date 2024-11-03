from __future__ import annotations
from dataclasses import dataclass
from flightanalysis.definition.maninfo.positioning import Direction
from flightanalysis.data import list_resources, get_json_resource, get_file
import pandas as pd

fcj_categories = {
    "F3A FAI": "f3a",
    "F3A": "f3a",
    "US AMA": "nsrca",
    "F3A UK": "f3auk",
    "F3A US": "nsrca",
    "IMAC": "imac",
}

fcj_schedules = {
    "P23": "p23",
    "F23": "f23",
    "P25": "p25",
    "F25": "f25",
    "Unlimited 2024": "unlimited2024",
}


def lookup(val, data):
    val = val.replace("_", " ")
    return data[val] if val in data else val


@dataclass
class ManDetails:
    name: str
    id: int
    k: float
    entry: Direction


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
    def lookupCategory(category):
        return lookup(category, fcj_categories)

    @staticmethod
    def lookupSchedule(schedule):
        return lookup(schedule, fcj_schedules)

    @staticmethod
    def mixed():
        return ScheduleInfo("na", "mixed")

    def fcj_to_pfc(self):
        return ScheduleInfo(
            lookup(self.category, fcj_categories), lookup(self.name, fcj_schedules)
        )

    def pfc_to_fcj(self):
        def rev_lookup(val, data):
            return (
                next(k for k, v in data.items() if v == val)
                if val in data.values()
                else val
            )

        return ScheduleInfo(
            rev_lookup(self.category, fcj_categories),
            rev_lookup(self.name, fcj_schedules),
        )

    @staticmethod
    def from_fcj_sch(sch):
        return ScheduleInfo(*sch).fcj_to_pfc()

    def to_fcj_sch(self):
        return list(self.pfc_to_fcj().__dict__.values())

    @staticmethod
    def build(category, name):
        return ScheduleInfo(category.lower(), name.lower())

    def file(self):
        return get_file(f"{str(self).lower()}_schedule.json")

    def json_data(self):
        return get_json_resource(self.file())["mdefs"]

    def manoeuvre_details(self) -> list[ManDetails]:
        mds = []

        for i, (k, v) in enumerate(self.json_data().items()):
            if isinstance(v, list):
                v = v[0]
            mds.append(
                ManDetails(
                    v["info"]["short_name"],
                    i + 1,
                    v["info"]["k"],
                    Direction.parse(v["info"]["start"]["direction"]),
                )
            )
        return mds

    def k_factors(self):
        return pd.Series({md.name: md.k for md in self.manoeuvre_details()}, name="k")

    def direction_definition(self):
        """returns a dict containing the id of the manoeuvre that should be used to figure out the direction
        the schedule is flown in and whether it should be upwind or downwind.
        This will be: {manid: 0, direction:UPWIND} unless the first manoevure is crossbox"""
        return get_json_resource(self.file())["direction_definition"]

    def __eq__(self, other: ScheduleInfo):
        return str(self.fcj_to_pfc()) == str(other.fcj_to_pfc())


schedule_library = [
    ScheduleInfo.from_str(fname) for fname in list_resources("schedule")
]
