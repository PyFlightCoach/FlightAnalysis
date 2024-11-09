from flightanalysis.definition import (
    ManDef,
    ManParm,
    ManParms,
    ElDef,
    ElDefs,
    Opp,
)
from typing import Callable
from functools import partial
import numpy as np
from flightanalysis.scoring.box import Box
from flightanalysis.scoring.downgrade import DowgradeGroups
from dataclasses import dataclass
from flightdata import State
from flightanalysis.elements import Loop, Line, Snap, Spin, StallTurn

class MBTags:
    CENTRE = 0


def centred(elb):
    setattr(elb, "centred", True)
    return elb


c45 = np.cos(np.radians(45))


def r(turns):
    return 2 * np.pi * np.array(turns)


@dataclass
class ManBuilder:
    mps: ManParms
    mpmaps: dict[str, dict]
    dg_applicator: Callable[[Loop | Line | Snap | Spin | StallTurn, State, str, str], list]
    Inter: object
    box: Box

    def __getattr__(self, name):
        if name in self.mpmaps:
            return partial(self.el, name)
        raise AttributeError(f"ManBuilder has no attribute {name}")

    def el(self, kind, *args, force_name=None, **kwargs):
        """Setup kwargs to pull defaults from mpmaps
        returns a function that appends the created elements to a ManDef"""

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
        maninfo,
        elmakers: list[Callable[[ManDef], ElDef]],
        relax_back=False,
        **kwargs,
    ) -> ManDef:
        mps = self.mps.copy()
        for k, v in kwargs.items():
            if isinstance(v, ManParm):
                mps.add(v)
            elif isinstance(k, str):
                if k in mps.data:
                    mps[k].defaul = v
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
