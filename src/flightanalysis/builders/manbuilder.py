from dataclasses import dataclass
from functools import partial
from typing import Callable

from schemas import ManInfo, Figure, PE, Option, Sequence

import numpy as np
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
from flightanalysis.elements import Line, Loop, Snap, Spin, StallTurn
from flightanalysis.scoring.box import Box
from flightanalysis.scoring.criteria import Combination


class MBTags:
    CENTRE = 0


def centred(elb):
    setattr(elb, "centred", True)
    return elb


c45 = np.cos(np.radians(45))


def r(turns):
    return (2 * np.pi * np.array(turns)).tolist()


@dataclass
class ManBuilder:
    mps: ManParms
    mpmaps: dict[str, dict]
    dg_applicator: Callable[
        [Loop | Line | Snap | Spin | StallTurn, State, str, str], list
    ]
    Inter: object
    box: Box

    def create_edef(self, pe: PE) -> ElDef:
        el = getattr(self, pe.kind)(*pe.args, **pe.kwargs)
        if pe.centred:
            el.centred = True
        return el

    def create_mdef(self, fig: Figure | Option) -> ManDef | ManOption:
        if isinstance(fig, Option):
            return ManOption([self.create_mdef(op) for op in fig.figures])
        else:
            return self.create(
                fig.info,
                [self.create_edef(pe) if isinstance(pe, PE) else pe for pe in fig.elements],
                **fig.ndmps,
            )

    def create_scheddef(self, seq: Sequence) -> SchedDef:
        return SchedDef([self.create_mdef(f) for f in seq.figures])

    def __getattr__(self, name):
        if name in self.mpmaps:
            return partial(self.el, name)
        raise AttributeError(f"ManBuilder has no attribute {name}")

    def el(self, kind, *args, force_name=None, **kwargs):
        """Setup kwargs to pull defaults from mpmaps
        returns a function that takes a ManDef, creats the eldefs and appends them to it"""

        all_kwargs = self.mpmaps[kind]["kwargs"].copy()  # take the defaults

        for k, a in kwargs.items():
            all_kwargs[k] = a  # take the **kwargs if they were specified

        all_kwargs.update(dict(zip(self.mpmaps[kind]["args"], args)))  # take the *args

        def append_el(md: ManDef, **kwargs) -> ElDefs:
            full_kwargs = {}
            for k, a in kwargs.items():
                full_kwargs[k] = ManParm.s_parse(a, md.mps)

            eds, mps = self.mpmaps[kind]["func"](
                force_name if force_name else md.eds.get_new_name(),
                **dict(**full_kwargs, Inter=self.Inter),
            )
            neds = md.eds.add(eds)
            md.mps.add(mps)
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
        self.line(force_name="entry_line", length=30)(md)

        for i, em in enumerate(elmakers, 1):
            if isinstance(em, int):
                if em == MBTags.CENTRE:
                    md.info.centre_points.append(len(md.eds.data))
            else:
                c1 = len(md.eds.data)
                try:
                    new_eds = em(md)
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

        md.mps = md.mps.remove_unused()
        return md.update_dgs(self.dg_applicator)




