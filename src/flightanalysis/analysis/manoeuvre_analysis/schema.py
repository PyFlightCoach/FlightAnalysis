from __future__ import annotations
from pydantic import BaseModel
from flightanalysis.definition.scheduleinfo import ScheduleInfo
from flightdata import fcj
from . import from_dict
from flightanalysis import __version__
import numpy as np
import pandas as pd


class MA(BaseModel):
    name: str
    id: int
    schedule: ScheduleInfo
    schedule_direction: str | None
    flown: list[dict] | dict

    mdef: dict | None = None
    manoeuvre: dict | None = None
    template: list[dict] | dict | None = None
    corrected: dict | None = None
    corrected_template: list[dict] | dict | None = None
    scores: dict | None = None

    history: dict[str, fcj.ManResult] | None = None

    def basic(self):
        return MA(
            name=self.name,
            id=self.id,
            schedule=self.schedule,
            schedule_direction=self.schedule_direction,
            flown=self.flown,
            history=self.history,
        )

    def run(
        self, basic: bool = True, optimise_aligment: bool = True, force: bool = False
    ) -> MA:
        version = __version__[1:] if __version__.startswith('v') else __version__
        if self.history and version in self.history and not force:
            return self
        else:
            man = from_dict(self.__dict__).proceed().run_all(optimise_aligment, True)
            return MA(
                **man.to_dict(basic),
                name=man.mdef.info.short_name,
                history={
                    **(self.history if self.history else {}),
                    **({version: fcj.ManResult.model_validate(man.fcj_results())} if man.__class__.__name__ == 'Scored' else {}),
                },
            )

    def simplify_history(self):
        vnames = [v[1:] if v.startswith("v") else v for v in self.history.keys()]
        vnames_old = vnames[::-1]
        vnids = [len(vnames) - vnames_old.index(vn) - 1 for vn in list(pd.Series(vnames).unique())]

        return MA(
            **(
                self.__dict__
                | dict(
                    history={vnames[i]: list(self.history.values())[i] for i in vnids}
                )
            )
        )


#        vids = [vnames.rindex(vn) for vn in set(vnames)]
