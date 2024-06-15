from __future__ import annotations
from dataclasses import dataclass
from ..el_analysis import ElementAnalysis
from flightdata import State
from flightanalysis.definition import ManDef, ScheduleInfo
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.scoring import Results, ManoeuvreResults, Measurement
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.definition.maninfo import Position
import numpy as np
from .alignment import Alignment
from loguru import logger


@dataclass
class Complete(Alignment):
    corrected: Manoeuvre
    corrected_template: State

    @staticmethod
    def from_dict(data:dict, fallback=True):
        pa = Alignment.from_dict(data, fallback)
        try:
            pa = Complete(
                **pa.__dict__,
                corrected=Manoeuvre.from_dict(data["corrected"]),
                corrected_template=State.from_dict(data["corrected_template"]),
            )
        except Exception as e:
            if fallback:
                logger.debug(f"Failed to parse Complete: {repr(e)}")
            else:
                raise e
        return pa

    def run(self, optimise_aligment=True) -> Scored:
        if optimise_aligment:
            self = self.optimise_alignment()
        self = self.update_templates()
        return Scored(**self.__dict__, 
            scores=ManoeuvreResults(self.inter(), self.intra(), self.positioning())
        )

    @property
    def elnames(self):
        return list(self.mdef.eds.data.keys())

    def __iter__(self):
        for elname in self.manoeuvre.all_elements().data.keys():
            yield self.get_ea(self.mdef.eds[elname])

    def __getitem__(self, i):
        return self.get_ea(['entry_line'] + self.mdef.eds[i] + ['exit_line'])

    def __getattr__(self, name):
        if name in self.mdef.eds.data.keys():
            return self.get_ea(self.mdef.eds[name])
        raise AttributeError(f'Attribute {name} not found in {self.__class__.__name__}')

    def get_ea(self, edef):
        el = getattr(self.manoeuvre.all_elements(), edef.name)
        st = el.get_data(self.flown)
        tp = el.get_data(self.template).relocate(st.pos[0])
        return ElementAnalysis(edef, self.mdef.mps, el, st, tp, el.ref_frame(tp))


    def update_templates(self):
        if not np.all(self.flown.element == self.template.element):    
            manoeuvre, template = self.manoeuvre.match_intention(self.template[0], self.flown)
            mdef = ManDef(self.mdef.info, self.mdef.mps.update_defaults(self.manoeuvre), self.mdef.eds)
            correction = mdef.create(self.template[0].transform).add_lines()

            return Complete(
                self.id, mdef, self.flown, self.direction,
                manoeuvre, template, correction, 
                correction.create_template(template[0])
            )
        else:
            return self
    
    def optimise_alignment(self):
        self.flown = self.manoeuvre.optimise_alignment(self.template, self.flown)
        return self.update_templates()
    
    def side_box(self):
        return F3A.intra.box(
            'side box', 
            Measurement.side_box(self.flown)
        )

    def top_box(self):
        return F3A.intra.box(
            'top box', 
            Measurement.top_box(self.flown)
        )

    def centre(self):
        results = Results('centres')
        for cpid in self.mdef.info.centre_points:
            results.add(F3A.single.angle(
                f'centre point {cpid}',
                Measurement.centre_box(self.flown.get_element(cpid+1)[0])
            ))

        for ceid, fac in self.mdef.info.centred_els:
            ce = self.flown.get_element(ceid+1)
            path_length = (abs(ce.vel) * ce.dt).cumsum()
            id = np.abs(path_length - path_length[-1] * fac).argmin()
            results.add(F3A.single.angle(
                f'centred element {ceid}',
                Measurement.centre_box(State(ce.data.iloc[[id], :]))
            ))

        if len(results) == 0 and self.mdef.info.position == Position.CENTRE:
            al = self.flown.get_element(slice(1,-1,None))
            midy = (self.flown.get_element(1).y[0] + self.flown.get_element(-1).y[-1]) / 2
            midid = np.abs(al.pos.y - midy).argmin()
            results.add(F3A.single.angle(
                'centred manoeuvre',
                Measurement.centre_box(al[midid])
            ))

        return results

    def distance(self):
        #TODO doesnt quite cover it, stalled manoeuvres could drift to > 170 for no downgrade
        return F3A.intra.depth(
            'distance',
            Measurement.depth(self.flown)
        )
        
    def intra(self):
        return self.manoeuvre.analyse(self.flown, self.template)

    def inter(self):
        return self.mdef.mps.collect(self.manoeuvre, self.template)

    def positioning(self):
        pres = Results('positioning')
        if self.mdef.info.position == Position.CENTRE:
            pres.add(self.centre())
        tp_width = max(self.corrected_template.y) - min(self.corrected_template.y)
        if tp_width < 10:
            pres.add(self.distance())
        tb = self.top_box()
        if tb.total > 0:
            pres.add(self.top_box())
        sb = self.side_box()
        if sb.total > 0:
            pres.add(self.side_box())
        return pres

    def plot_3d(self, **kwargs):
        from flightplotting import plotsec, plotdtw
        fig = plotdtw(self.flown, self.flown.data.element.unique())
        return plotsec(self.flown, color="blue", nmodels=20, fig=fig, **kwargs)



from .scored import Scored  # noqa: E402