from dataclasses import dataclass

from .el_analysis import ElementAnalysis
from flightdata import State, Flight, Origin
from flightanalysis.definition import ManDef, SchedDef
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.scoring import Results, Result, ManoeuvreResults
from flightanalysis.scoring.criteria.f3a_criteria import F3A
from flightanalysis.definition.maninfo import Position
import geometry as g
import numpy as np
from json import load


@dataclass
class PartialAnalysis:
    mdef: ManDef
    fl: State


@dataclass
class ManoeuvreAnalysis:
    mdef: ManDef
    aligned: State
    manoeuvre: Manoeuvre
    template: State
    corrected: Manoeuvre
    corrected_template: State
    
    def __getitem__(self, i):
        return self.get_ea(self.mdef.eds[i])

    def __getattr__(self, name):
        if name in self.mdef.eds.data.keys():
            return self.get_ea(self.mdef.eds[name])
        raise AttributeError()

    def get_ea(self, edef):
        el = getattr(self.manoeuvre.elements, edef.name)
        st = el.get_data(self.aligned)
        tp = el.get_data(self.template).relocate(st.pos[0])
        return ElementAnalysis(edef, self.mdef.mps, el, st, tp, el.ref_frame(tp))

    @property
    def uid(self):
        return self.mdef.uid

    @staticmethod
    def initial_transform(mdef: ManDef, flown: State) -> g.Transformation:
        initial = flown[0]
        return g.Transformation(
            initial.pos,
            mdef.info.start.initial_rotation(
                mdef.info.start.d.get_wind(initial.direction()[0])
        ))
    
    @staticmethod
    def basic_manoeuvre(mdef: ManDef, itrans: g.Transformation) -> tuple[Manoeuvre, State]:
        man = mdef.create(itrans).add_lines()
        return man, man.create_template(itrans)

    @staticmethod
    def alignment(manoeuvre: State, man: Manoeuvre, flown: State, radius=10, replace=False) -> tuple[float, State]:
        if 'element' in flown.label_cols:
            return True, -1, flown
        dist, aligned = State.align(flown, manoeuvre, radius=10)
        int_tp = man.match_intention(manoeuvre[0], aligned)[1]
        try:
            return True, *State.align(aligned, int_tp, radius=radius, mirror=False)
        except Exception as e:
            return False, dist, aligned

    @staticmethod
    def intention(man: Manoeuvre, aligned: State, manoeuvre: State) -> tuple[Manoeuvre, State]:
        return man.match_intention(manoeuvre[0], aligned)
            
    @staticmethod
    def alignment_optimisation(manoeuvre: Manoeuvre, template: State, aligned: State):
        return manoeuvre.optimise_alignment(template[0], aligned)
    
    @staticmethod
    def correction(mdef: ManDef, manoeuvre: Manoeuvre, int_tp: State) -> tuple[ManDef, Manoeuvre]:
        mdef = ManDef(mdef.info, mdef.mps.update_defaults(manoeuvre), mdef.eds)
        return mdef, mdef.create(int_tp[0].transform).add_lines()

    @staticmethod
    def from_pa(pa: PartialAnalysis):
        return ManoeuvreAnalysis.build(pa.mdef, pa.fl)
    
    @staticmethod
    def build(mdef: ManDef, flown: State):
        itrans = ManoeuvreAnalysis.initial_transform(mdef, flown)
        man, tp = ManoeuvreAnalysis.basic_manoeuvre(mdef, itrans)
        success, dist, aligned = ManoeuvreAnalysis.alignment(tp, man, flown)
        if not success:
            return PartialAnalysis(mdef, aligned)
        manoeuvre, int_tp = ManoeuvreAnalysis.intention(man, aligned, tp)
        mdef, corr = ManoeuvreAnalysis.correction(mdef, manoeuvre, int_tp)
        manoeuvre = manoeuvre.copy_directions(corr)
        int_tp = manoeuvre.el_matched_tp(int_tp[0], aligned)
        return ManoeuvreAnalysis(mdef, aligned, manoeuvre, int_tp, corr, corr.create_template(int_tp[0], aligned))  
    
    def optimise_alignment(self):
        aligned = self.alignment_optimisation(self.manoeuvre, self.template, self.aligned)
        manoeuvre, int_tp = ManoeuvreAnalysis.intention(self.manoeuvre, aligned, self.template)
        mdef, corr = ManoeuvreAnalysis.correction(self.mdef, manoeuvre, int_tp)
        return ManoeuvreAnalysis(mdef, aligned, manoeuvre, int_tp, corr, 
                                 corr.create_template(int_tp[0], aligned))
    
    def plot_3d(self, **kwargs):
        from flightplotting import plotsec, plotdtw
        fig = plotdtw(self.aligned, self.aligned.data.element.unique())
        #fig = plotsec(self.template, color="red", nmodels=20, fig=fig, **kwargs)
        return plotsec(self.aligned, color="blue", nmodels=20, fig=fig, **kwargs)
        
    def side_box(self):
        al = self.aligned#.get_element(slice(1,-1,None))
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
        top_box_angle = np.arctan(self.aligned.pos.z / self.aligned.pos.y)
        tb = max(top_box_angle)
        outside_tb = (tb - 1.0471975511965976) / 1.0471975511965976
        top_box_dg = max(outside_tb, 0) * 6
        return Result("top box", [tb], [], [outside_tb], [top_box_dg], [])

    def centre(self):
        centres = []
        centre_names = []
        for cpid in self.mdef.info.centre_points:
            if cpid == 0:
                centre_pos = self.manoeuvre.elements[cpid].get_data(self.aligned).pos[0]
            else:
                centre_pos = self.manoeuvre.elements[cpid-1].get_data(self.aligned).pos[-1]
            centres.append(np.arctan2(centre_pos.x, centre_pos.y)[0])
            centre_names.append(f'centre point {cpid}')

        for ceid, fac in self.mdef.info.centred_els:
            ce = self.manoeuvre.elements[ceid].get_data(self.aligned)
            centre_pos = ce.pos[int(len(ce) * fac)]
            centres.append(np.arctan2(centre_pos.x, centre_pos.y)[0])
            centre_names.append(f'centred el {ceid}')

        if len(centres) == 0:
            al = self.aligned.get_element(slice(1,-1,None))
            side_box_angle = np.arctan2(al.pos.x, al.pos.y)
            centres.append(max(side_box_angle) + min(side_box_angle))
            centre_names.append(f'global centre')

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
        dist_key = np.argmax(self.aligned.pos.y)
        dist = self.aligned.pos.y[dist_key]
        
        dist_dg = F3A.single.distance.lookup(max(dist, 170) - 170)
        
        return Result("distance", [], [],[dist],[dist_dg],dist_key)

    def intra(self):
        return self.manoeuvre.analyse(self.aligned, self.template)

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

    def scores(self):
        return ManoeuvreResults(
            self.inter(), 
            self.intra(), 
            self.positioning()
        )
    
    @staticmethod
    def from_fcj(file: str, mid: int):
        with open(file, 'r') as f:
            data = load(f)
        flight = Flight.from_fc_json(data)
        box = Origin.from_fcjson_parmameters(data["parameters"])

        sdef = SchedDef.load(data["parameters"]["schedule"][1])

        state = State.from_flight(flight, box).splitter_labels(
            data["mans"],
            [m.info.short_name for m in sdef]
        )
        mdef= sdef[mid]
        return ManoeuvreAnalysis.build(
            mdef, 
            state.get_manoeuvre(mdef.info.short_name)
        )

    def to_dict(self, scores: bool = False):
        res = dict(
            mdef = self.mdef.to_dict(),
            aligned = self.aligned.to_dict(),
            manoeuvre = self.manoeuvre.to_dict(),
            template = self.template.to_dict(),
            corrected = self.corrected.to_dict(),
            corrected_template = self.corrected_template.to_dict()
        )
        if scores:
            res['score'] = self.scores().to_dict()
        return res

    @staticmethod
    def from_fcs_dict(data: dict, newmdef: ManDef=None):
        mdef = ManDef.from_dict(data["mdef"]) if newmdef is None else newmdef
        
        try:
            return ManoeuvreAnalysis(
                mdef,
                State.from_dict(data["aligned"]),
                Manoeuvre.from_dict(data["manoeuvre"]),
                State.from_dict(data["template"]),
                Manoeuvre.from_dict(data["corrected"]),
                State.from_dict(data["corrected_template"]),
            )
        except KeyError as ex:
            print(ex)
            return PartialAnalysis(
                ManDef.from_dict(data["mdef"]),
                State.from_dict(data["fl"]),
            )
    
    @staticmethod
    def from_dict(data:dict):
        return ManoeuvreAnalysis(
            ManDef.from_dict(data["mdef"]),
            State.from_dict(data["aligned"]),
            Manoeuvre.from_dict(data["manoeuvre"]),
            State.from_dict(data["template"]),
            Manoeuvre.from_dict(data["corrected"]),
            State.from_dict(data["corrected_template"]),
        )
