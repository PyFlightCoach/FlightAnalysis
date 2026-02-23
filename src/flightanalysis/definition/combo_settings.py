from __future__ import annotations

from flightdata.base.collection import Collection

from .combo_setting import ComboSetting


class ComboSettings(Collection):
    """A collection of ComboSetting objects, keyed on the manparm name, so only one setting is allowed per manparm."""

    VType = ComboSetting
    uid = "mp_name"

    def set_values(self, **kwargs):
        """Return a new ComboSettings with the values set to the provided kwargs."""
        return ComboSettings(
            [
                s.update(kwargs[s.mp_name]) if s.mp_name in kwargs else s
                for s in self.values()
            ]
        )

    def __str__(self):
        return ",".join([str(s) for s in self.values()])

    def __repr__(self):
        return f"ComboSettings({str(self)})"

    def to_dict(self):
        return {s.mp_name: s.value for s in self.values()}

    def mp_names(self):
        return {s.mp_name for s in self.values()}

    @staticmethod
    def parse(data: str):
        return ComboSettings(
            [
                ComboSetting(mp_name, int(value))
                for mp_name, value in (s.split(".") for s in data.split(","))
            ]
        )

    def includes(self, other: ComboSettings):
        """Return True if this ComboSettings includes all the settings in the other ComboSettings."""
        return all(s in self.values() for s in other.values())

    def check(self, other: ComboSettings | ComboSetting | None):
        """Return true if this combosettings is not excluded by the other, or vice versa"""

        if other is None:
            return True
        elif isinstance(other, ComboSettings):
            return all(self.check(o) for o in other)
        else:
            if (
                other.mp_name in self.keys()
                and not other.value == self[other.mp_name].value
            ):
                return False
            else:
                return True

    def __eq__(self, other: ComboSettings):
        s1 = set([str(s) for s in self.values()])
        s2 = set([str(s) for s in other.values()])
        return s1 == s2

    def add_throw_duplicate(self, combo: ComboSetting | ComboSettings, inplace=True):
        if self.check(combo):
            return self.add(combo, inplace)
        else:
            raise ValueError(
                f"Combo {combo} already exists in ComboSettings with a different value: {self[combo.mp_name]}"
            )


class ComboSet(Collection):
    """A collection of ComboSetting objects, keyed on the manparm name and value, so multiple settings for the same manparm are allowed."""

    VType = ComboSetting
    uid = "uid"

    def __repr__(self):
        return f"ComboSet({[str(s) for s in self.values()]})"

    def mps(self):
        return {s.mp_name for s in self.values()}

    def collect_mp(self, mp_name: str):
        return {s.value for s in self.values() if s.mp_name == mp_name}

    def __str__(self):
        return ",".join([str(s) for s in self.values()])

    def __eq__(self, other):
        return set(list(self.values())) == set(list(other.values()))
