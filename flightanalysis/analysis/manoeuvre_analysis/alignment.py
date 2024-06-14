from __future__ import annotations
from dataclasses import dataclass
from flightdata import State
from flightanalysis.manoeuvre import Manoeuvre
from loguru import logger
from .basic import Basic
from flightanalysis.definition import ManDef, ScheduleInfo
from ..el_analysis import ElementAnalysis

@dataclass
class Alignment(Basic):
    manoeuvre: Manoeuvre | None
    template: State | None

    def __getattr__(self, name) -> ElementAnalysis:
        return ElementAnalysis(
            self.mdef.data[name],
            self.mdef.mps,
            self.manoeuvre.elements.data[name],
            self.flown.get_element(name),
            self.template.get_element(name),
            self.template.get_element(name)[0].transform
        )

    def run_all(self, optimise_aligment=True, force=False) -> Alignment | Complete | Scored:
        if self.__class__.__name__ == 'Scored' and force:
            self = self.downgrade()
        new = self
        while self.__class__.__name__ != 'Scored':
            new = self.run(optimise_aligment) if isinstance(self, Complete) else self.run()
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

    def run(self) -> Alignment | Complete:
        if 'element' not in self.flown.data.columns:
            try:
                self = self._run(True)[1]
            except Exception as e:
                logger.error(f'Failed to run alignment stage 1: {repr(e)}')
                return self
        try:
            return self._run(False)[1].proceed()
        except Exception as e:
            logger.error(f'Failed to run alignment stage 2: {repr(e)}')
            return self

    def _run(self, mirror=False, radius=10) -> Alignment:
        dist, aligned = State.align(self.flown, self.template, radius, mirror)
        return dist, self.update(aligned)

    def update(self, aligned: State) -> Alignment:
        man, tp = self.manoeuvre.match_intention(self.template[0], aligned)
        mdef = ManDef(self.mdef.info, self.mdef.mps.update_defaults(man), self.mdef.eds)
        return Alignment(self.id, mdef, aligned, self.direction, man, tp)

    def _proceed(self) -> Complete:
        if 'element' in self.flown.data.columns:
            correction = self.mdef.create(self.template[0].transform)
            return Complete(
                self.id, self.mdef, self.flown, self.direction, 
                self.manoeuvre, self.template, correction, 
                correction.create_template(self.template[0], self.flown)
            )
        else:
            return self

    def to_mindict(self, sinfo: ScheduleInfo=None, full=False):
        data = dict(
            els = self.flown.label_ranges('element').to_dict('records')
        )
        if full:
            data = dict(
                **super().to_mindict(sinfo),
                **data
            )
        return data
        
from .complete import Complete  # noqa: E402
from .scored import Scored  # noqa: E402