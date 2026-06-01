from __future__ import annotations

from flightanalysis.elements.tags import DGTags
from dataclasses import dataclass
from typing import ClassVar, Any
from ..reffuncs import measures as me, selectors as se
from ..criteria import Criteria


@dataclass
class DG:
    name: str
    display_name: str | None
    tags: DGTags | None
    ENABLE_VISIBILITY: ClassVar[bool] = True
    eds: list[str] | None

    def from_dict(data: dict[str, Any], eds: list[str]=None):
        tags = DGTags.from_dict(data["tags"]) if "tags" in data and data["tags"] else None
        if "first" in data:
            return PairedDowngrade(
                name=data["name"],
                display_name=data.get("display_name"),
                tags=tags,
                first=DG.from_dict(data["first"]),
                second=DG.from_dict(data["second"]),
                eds = eds
            )
        elif "measure" in data:
            return DownGrade(
                name=data["name"],
                display_name=data.get("display_name"),
                tags=tags,
                measure=me.parse(data["measure"]),
                selectors=se.parse(data["selectors"]),
                criteria=Criteria.from_dict(data["criteria"]),
                eds = eds
            )
        else:
            raise ValueError("Invalid downgrade data")


from .downgrade import DownGrade  # noqa: E402
from .downgrade_pair import PairedDowngrade  # noqa: E402
