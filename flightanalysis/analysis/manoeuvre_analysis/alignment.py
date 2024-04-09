from __future__ import annotations
from dataclasses import dataclass
from flightdata import State
from flightanalysis.manoeuvre import Manoeuvre
from loguru import logger
from .basic import AlinmentStage, Basic
from flightanalysis.definition import ManDef


@dataclass
class Alignment(Basic):
    manoeuvre: Manoeuvre
    template: State

    def run_all(self):
        while self.__class__.__name__ != 'Scored':
            new = self.run()
            if new.__class__.__name__ == self.__class__.__name__:
                break
            self = new
        return new
    
    @staticmethod
    def from_dict(data: dict, fallback=True):
        ia = Basic.from_dict(data)
        try:    
            ia = Alignment(
                manoeuvre=Manoeuvre.from_dict(data['manoeuvre']),
                template=State.from_dict(data['template']),
                **ia.__dict__
            )
        except Exception as e:
            if fallback:
                logger.debug(f'Failed to parse Alignment {repr(e)}')
            else:
                raise e
        return ia

    def alignment(self, radius=10):
        assert self.stage < AlinmentStage.SECONDARY
        logger.debug(f'Running alignment stage {self.stage}')
        aligned = State.align(self.flown, self.template, radius, self.stage==AlinmentStage.SETUP)[1]
        return Alignment(
            self.mdef, aligned, self.direction, self.stage + 1,
            *self.manoeuvre.match_intention(self.template[0], aligned)
        )

    def run_alignment(self, radius=10):
        while self.stage < AlinmentStage.SECONDARY:
            try:
                self = self.alignment(radius)
            except Exception as ex:
                logger.exception(f'Error running alignment stage {self.stage}, {ex}')
                break
        return self

    def run(self) -> Complete:
        self = self.run_alignment()
        if self.stage < AlinmentStage.SECONDARY:
            return self
        else:
            mdef = ManDef(self.mdef.info, self.mdef.mps.update_defaults(self.manoeuvre), self.mdef.eds)
            correction = mdef.create(self.template[0].transform).add_lines()

            return Complete(
                mdef, self.flown, self.direction, AlinmentStage.SECONDARY, 
                self.manoeuvre, self.template, correction, 
                correction.create_template(self.template[0], self.flown)
            )

from .complete import Complete  # noqa: E402
