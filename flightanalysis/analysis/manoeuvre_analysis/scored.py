from dataclasses import dataclass
from .complete import Complete
from flightanalysis.scoring import ManoeuvreResults
from flightanalysis.definition.scheduleinfo import ScheduleInfo
from loguru import logger


@dataclass
class Scored(Complete):
    scores: ManoeuvreResults

    def downgrade(self) -> Complete:
        return Complete(
            self.id, self.mdef, self.flown, self.direction, 
            self.manoeuvre, self.template, self.corrected, 
            self.corrected_template
        )
    
    def to_dict(self):
        return dict(
            **super().to_dict(),
            scores=self.scores.to_dict()
        )


    @staticmethod
    def from_dict(data:dict, fallback=True):
        ca = Complete.from_dict(data, fallback)
        try:
            ca = Scored(
                **ca.__dict__,
                scores=ManoeuvreResults.from_dict(data["scores"])
            )
        except Exception as e:
            if fallback:
                logger.debug(f"Failed to read scores, {repr(e)}")
            else:
                raise e
        return ca
        
    def to_mindict(self, sinfo: ScheduleInfo=None, full=False):
        data = dict(
            **super().to_mindict(sinfo, full),
            scores=dict(
                **self.scores.summary(),
                total=self.scores.score(),
                k=self.mdef.info.k
            )
        )
        
        return data
    
    def fcj_results(self):
        return dict(
            **super().fcj_results(),
            results=self.scores.fcj_results()
        )