from __future__ import annotations

from flightanalysis.elements.tags import DGTags
from dataclasses import dataclass
from typing import ClassVar, Any
<<<<<<< HEAD
from ..reffuncs import measures as me, selectors as se, smoothers as sm
=======
from ..reffuncs import measures as me, selectors as se, visors as vi
>>>>>>> newmeasure
from ..criteria import Criteria


@dataclass
class DG:
    name: str
    tags: DGTags | None
    ENABLE_VISIBILITY: ClassVar[bool] = True

    def from_dict(data: dict[str, Any]):
        tags = DGTags.from_dict(data["tags"]) if "tags" in data and data["tags"] else None
        if "first" in data:
            return PairedDowngrade(
                name=data["name"],
                tags=tags,
                first=DG.from_dict(data["first"]),
                second=DG.from_dict(data["second"]),
            )
        elif "measure" in data:
            return DownGrade(
                name=data["name"],
                tags=tags,
                measure=me.parse(data["measure"]),
                smoothers=sm.parse(data["smoothers"]),
                selectors=se.parse(data["selectors"]),
                criteria=Criteria.from_dict(data["criteria"]),
            )
        else:
            raise ValueError("Invalid downgrade data")


from .downgrade import DownGrade  # noqa: E402
from .downgrade_pair import PairedDowngrade  # noqa: E402
