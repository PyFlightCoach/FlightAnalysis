from dataclasses import dataclass
from functools import partial
from typing import Callable, Tuple

from schemas import ManInfo, Figure, PE, Option, Sequence
from schemas.positioning import MBTags

import pandas as pd
from flightdata import State

from flightanalysis.definition import (
    ElDef,
    ElDefs,
    ManDef,
    ManParm,
    ManParms,
    ManOption,
    SchedDef
)
from flightanalysis.elements import Line, Loop, Snap, Spin, StallTurn, TailSlide
from flightanalysis.scoring.box import Box
from flightanalysis.scoring.criteria import Combination



@dataclass
class ManBuilder:
    mps: ManParms
    mpmaps: dict[str, dict]
    dg_applicator: Callable[
        [Loop | Line | Snap | Spin | StallTurn, TailSlide, State, str, str], list
    ]
    Inter: object
    box: Box

    def create_eb(self, pe: PE) -> ElDef:
        el = getattr(self, pe.kind)(*pe.args, **pe.kwargs)
        if pe.centred:
            el.centred = True
        return el

    def create_mdef(self, fig: Figure | Option) -> ManDef | ManOption:
        try:
            if isinstance(fig, Option):
                return ManOption([self.create_mdef(op) for op in fig.figures])
            else:
                return self.create(
                    fig.info,
                    [self.create_eb(pe) if isinstance(pe, PE) else pe for pe in fig.elements],
                    fig.relax_back,
                    **fig.ndmps,
                )
        except Exception as ex:
            raise Exception(f"Error creating ManDef for {fig.info.name}") from ex

    def create_scheddef(self, seq: Sequence) -> SchedDef:
        return SchedDef([self.create_mdef(f) for f in seq.figures])

    def __getattr__(self, name):
        if name in self.mpmaps:
            return partial(self.el, name)
        raise AttributeError(f"ManBuilder has no attribute {name}")

    def el(self, kind, *args, force_name=None, **kwargs):
        """Setup kwargs to pull defaults from mpmaps
        returns a function that creats a new eldef and updates the mps"""

        all_kwargs = self.mpmaps[kind]["kwargs"].copy()  # take the defaults

        for k, a in kwargs.items():
            all_kwargs[k] = a  # take the **kwargs if they were specified

        all_kwargs.update(dict(zip(self.mpmaps[kind]["args"], args)))  # take the *args

        def append_el(eds: ElDefs, mps: ManParms, **kwargs) -> Tuple[ElDefs, ManParms]:
            full_kwargs = {}
            for k, a in kwargs.items():
                full_kwargs[k] = ManParm.s_parse(a, mps)

            neds, nmps = self.mpmaps[kind]["func"](
                force_name if force_name else eds.get_new_name(),
                **dict(**full_kwargs, Inter=self.Inter),
            )
            #neds = eds.add(eds)
            mps.add(nmps)
            return neds

        return partial(append_el, **all_kwargs)

    def create(
        self,
        maninfo: ManInfo,
        elmakers: list[Callable[[ManDef], ElDef]],
        relax_back=False,
        **kwargs,
    ) -> ManDef:
        mps = self.mps.copy()
        for k, v in kwargs.items():
            if isinstance(v, ManParm): # add a new manparm
                mps.add(v) 
            else:
                if k in mps.data: # update the default value
                    mps[k].defaul = v 
                else: # create and add a manparm
                    if pd.api.types.is_list_like(v):
                        mps.add(ManParm(k, Combination(desired=v), 0, "rad"))
                    else:
                        mps.add(ManParm.parse(v, mps, k))

        md = ManDef(
            maninfo,
            mps,
            ElDefs(),
            self.box.__class__(**dict(self.box.__dict__, relax_back=relax_back)),
        )
        md.eds.add(self.line(force_name="entry_line", length=30)(md.eds, md.mps))

        for i, em in enumerate(elmakers, 1):
            if isinstance(em, int):
                if em == MBTags.CENTRE:
                    md.info.centre_points.append(len(md.eds.data))
            else:
                c1 = len(md.eds.data)
                try:
                    new_eds = md.eds.add(em(md.eds, md.mps))
                except Exception as ex:
                    raise Exception(
                        f"Error running elmaker {i} of {md.info.name}"
                    ) from ex

                c2 = len(md.eds.data)

                if hasattr(em, "centred"):
                    if c2 - c1 == 1:
                        md.info.centred_els.append((c1, 0.5))

                    else:
                        ceid, fac = ElDefs(new_eds).get_centre(mps)
                        if abs(int(fac) - fac) < 0.05:
                            md.info.centre_points.append(c1 + ceid + int(fac))
                        else:
                            md.info.centred_els.append((ceid + c1, fac))
        collmps = md.mps.remove_unused()
        propmps = md.mps.subset(md.eds.list_props())
        md.mps = ManParms.merge([collmps, propmps])
        return md.update_dgs(self.dg_applicator)




