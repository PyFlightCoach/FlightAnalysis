from dataclasses import dataclass
from .complete import Complete
from flightanalysis.scoring import ManoeuvreResults
from loguru import logger


@dataclass
class Scored(Complete):
    scores: ManoeuvreResults

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
    
    def run(self, optimise_alignment=True):
        return self