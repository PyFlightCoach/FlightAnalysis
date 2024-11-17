from __future__ import annotations
from dataclasses import dataclass
from flightanalysis.scoring import ManoeuvreResults
from .complete import Complete


@dataclass
class Scored(Complete):
    scores: ManoeuvreResults

    def downgrade(self) -> Complete:
        return Complete(
            self.id,
            self.schedule_direction,
            self.flown,
            self.mdef,
            self.manoeuvre,
            self.template,
            self.corrected,
            self.corrected_template,
        )


    @staticmethod
    def from_dict(ajman: dict) -> Scored:
        analysis = Complete.from_dict(ajman)
        if isinstance(analysis, Complete) and ajman["scores"]:
            return Scored(
                **analysis.__dict__, scores=ManoeuvreResults.from_dict(ajman["scores"])
            )
        else:
            return analysis

    def to_dict(self, basic: bool=False) -> dict:
        _basic = super().to_dict(basic)  # , sinfo, dict(**history, **self.fcj_results()))
        if basic:
            return _basic
        return dict(**_basic, scores=self.scores.to_dict())

    def fcj_results(self):
        return dict(**super().fcj_results(), results=self.scores.fcj_results())

    