"""
An ElTag describes some characteristic of an element
Downgrades are applied to elements based on their tags

A tag string is a comma-separated list to check against a set of ElTags
all entries in the list must be true
a single Eltag (eg ROLL) is true if it is present 
preceding with ! means it must not be present
logicial or (|) is allowed within an entry
e.g. "LINE | LOOP, HORIZONTAL, !ENTRYLINE"
spaces are ignored

returns a function that takes a set of ElTags and returns True or False
"""
from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class ElTag(Enum):
    ANY = auto()
    LINE = auto()
    LOOP = auto()
    SNAP = auto()
    SPIN = auto()
    STALLTURN = auto()
    TAILSLIDE = auto()
    ROLL = auto()
    NONE = auto()
    HORIZONTAL = auto()
    HORIZONTALENTRY = auto()
    HORIZONTALEXIT = auto()
    VERTICAL = auto()
    VERTICALENTRY = auto()
    VERTICALEXIT = auto()
    LOOPSEQUENCE = auto()



@dataclass
class TagCheck:
    tag: ElTag
    has: bool = True

    @staticmethod
    def parse(tagstr: str):
        tagstr = tagstr.strip()
        if tagstr.startswith("!"):
            return TagCheck(ElTag[tagstr[1:].upper()], has=False)
        elif len(tagstr) == 0:
            return TagCheck(ElTag.ANY, has=True)
        else:
            return TagCheck(ElTag[tagstr.upper()], has=True)

    def __call__(self, tags: set[ElTag]) -> bool:
        if self.tag == ElTag.ANY:
            return True
        elif self.has:
            return self.tag in tags
        else:
            return self.tag not in tags

    def __str__(self):
        return f"{'' if self.has else '!'}{self.tag.name}"

@dataclass
class TagCheckOr:
    checks: list[TagCheck]

    @property
    def tags(self) -> set[ElTag]:
        return {check.tag for check in self.checks}

    def __call__(self, tags: set[ElTag]) -> bool:
        return any(check(tags) for check in self.checks)
    
    def parse(tagstr: str):
        return TagCheckOr([TagCheck.parse(p) for p in tagstr.split("|")])

    def __str__(self):
        return " | ".join(str(c) for c in self.checks)

@dataclass 
class TagCheckAnd:
    checks: list[TagCheckOr]

    @property
    def tags(self) -> set[ElTag]:
        _tags = set()
        for check in self.checks:
            _tags.update(check.tags)
        return _tags

    def __call__(self, tags: set[ElTag]) -> bool:
        return all(check(tags) for check in self.checks)
    
    def parse(tagstr: str):
        return TagCheckAnd([TagCheckOr.parse(p) for p in tagstr.split(",")])

    def __str__(self):
        return ", ".join(str(c) for c in self.checks)

@dataclass
class DGTags:
    last: TagCheckAnd
    this: TagCheckAnd
    next: TagCheckAnd

    def __call__(self, last_tags: set[ElTag], this_tags: set[ElTag], next_tags: set[ElTag]) -> bool:
        return self.last(last_tags) and self.this(this_tags) and self.next(next_tags)

    def parse(last: str, this: str, next: str) -> DGTags:
        return DGTags(
            last=TagCheckAnd.parse(last),
            this=TagCheckAnd.parse(this),
            next=TagCheckAnd.parse(next),
        )

    def to_dict(self) -> dict:
        return dict(
            last=str(self.last),
            this=str(self.this),
            next=str(self.next),
        )
    @staticmethod
    def from_dict(data: dict) -> DGTags:
        return DGTags(
            last=TagCheckAnd.parse(data["last"]),
            this=TagCheckAnd.parse(data["this"]),
            next=TagCheckAnd.parse(data["next"]),
        )