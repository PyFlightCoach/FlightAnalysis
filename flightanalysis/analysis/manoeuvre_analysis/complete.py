from __future__ import annotations
from dataclasses import dataclass
from ..el_analysis import ElementAnalysis
from flightdata import State
from flightanalysis.definition import ManDef
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.elements import Element
from flightanalysis.scoring import Results, Result, ManoeuvreResults
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.definition.maninfo import Position
import numpy as np
from .alignment import Alignment, AlinmentStage
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
                logger.exception(f"Failed to parse Complete: {repr(e)}")
            else:
                raise e
        return pa

    def run(self) -> Scored:
        if self.stage < AlinmentStage.OPTIMISED:
            self = self.optimise_alignment()
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

    def optimise_alignment(self):
        aligned = self.manoeuvre.optimise_alignment(self.template, self.flown)
        manoeuvre, template = self.manoeuvre.match_intention(self.template[0], aligned)
        mdef = ManDef(self.mdef.info, self.mdef.mps.update_defaults(self.manoeuvre), self.mdef.eds)
        correction = mdef.create(self.template[0].transform).add_lines()

        return Complete(
            mdef, aligned, self.direction, AlinmentStage.OPTIMISED, 
            manoeuvre, template, correction, correction.create_template(template[0])
        )
    
    def side_box(self):
        al = self.flown
        side_box_angle = np.arctan2(al.pos.x, al.pos.y)

        max_sb = max(abs(side_box_angle))
        min_sb = min(abs(side_box_angle))

        outside = 1 - (1.0471975511965976 - min_sb) / (max_sb - min_sb)
        box_dg = max(outside, 0.0) * 5.0
        return Result(
            "side box",
            [max_sb, min_sb],
            [],
            [outside],
            [box_dg],
            []
        )

    def top_box(self):
        top_box_angle = np.arctan(self.flown.pos.z / self.flown.pos.y)
        tb = max(top_box_angle)
        outside_tb = (tb - 1.0471975511965976) / 1.0471975511965976
        top_box_dg = max(outside_tb, 0) * 6
        return Result("top box", [tb], [], [outside_tb], [top_box_dg], [])

    def centre(self):
        centres = []
        centre_names = []
        for cpid in self.mdef.info.centre_points:
            if cpid == 0:
                centre_pos = self.manoeuvre.elements[cpid].get_data(self.flown).pos[0]
            else:
                centre_pos = self.manoeuvre.elements[cpid-1].get_data(self.flown).pos[-1]
            centres.append(np.arctan2(centre_pos.x, centre_pos.y)[0])
            centre_names.append(f'centre point {cpid}')

        for ceid, fac in self.mdef.info.centred_els:
            ce = self.manoeuvre.elements[ceid].get_data(self.flown)
            centre_pos = ce.pos[int(len(ce) * fac)]
            centres.append(np.arctan2(centre_pos.x, centre_pos.y)[0])
            centre_names.append(f'centred el {ceid}')

        if len(centres) == 0:
            al = self.flown.get_element(slice(1,-1,None))
            side_box_angle = np.arctan2(al.pos.x, al.pos.y)
            centres.append(max(side_box_angle) + min(side_box_angle))
            centre_names.append('global centre')

        results = Results('centres')
        for centre, cn in zip(centres, centre_names):
            results.add(Result(
                cn,[],[],[centre],
                [F3A.single.angle.lookup(abs(centre))],
                [0]
            ))
        return results

    def distance(self):
        #TODO doesnt quite cover it, stalled manoeuvres could drift to > 170 for no downgrade
        dist_key = np.argmax(self.flown.pos.y)
        dist = self.flown.pos.y[dist_key]
        
        dist_dg = F3A.single.distance.lookup(max(dist, 170) - 170)
        
        return Result("distance", [], [],[dist],[dist_dg],dist_key)

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
        pres.add(self.top_box())
        pres.add(self.side_box())
        return pres

    def plot_3d(self, **kwargs):
        from flightplotting import plotsec, plotdtw
        fig = plotdtw(self.flown, self.flown.data.element.unique())
        return plotsec(self.flown, color="blue", nmodels=20, fig=fig, **kwargs)



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
                logger.exception(f"Failed to read scores, {repr(e)}")
            else:
                raise e
        return ca