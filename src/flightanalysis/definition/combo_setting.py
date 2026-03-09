from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ComboSetting:
    mp_name: str
    value: int

    def to_dict(self):
        return str(self)
    
    @staticmethod
    def from_dict(data: str):
        mp_name, value = data.split(".")
        return ComboSetting(mp_name, int(value))

    def __str__(self):
        return f"{self.mp_name}.{self.value}"

    def update(self, new_value: int) -> ComboSetting:
        return ComboSetting(self.mp_name, new_value)

    def __eq__(self, other: ComboSetting):
        return self.mp_name == other.mp_name and self.value == other.value
    
    def __repr__(self):
        return str(self)

    @property
    def uid(self):
        return str(self)