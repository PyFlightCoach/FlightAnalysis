from __future__ import annotations
from tomllib import load
from pathlib import Path
from dataclasses import dataclass, replace
from functools import partial
from typing import Callable, Tuple, NamedTuple, Any
from flightanalysis.scoring.box import TriangularBox, RectangularBox
from flightanalysis.scoring.criteria.exponential import parse_expos_from_csv
from flightanalysis.scoring.downgrade.downgrades import parse_downgrade_csv
from flightanalysis.scoring.criteria import parse_criteria_csv, Combination
from flightanalysis.scoring.box.parser import parse_box_downgrades, parse_box
from loguru import logger
from schemas import ManInfo, Figure, PE, Option, Sequence
from inspect import getfullargspec
from schemas.positioning import MBTags
import numpy as np
import pandas as pd

from flightanalysis.definition import (
    ElDef,
    ElDefs,
    ManDef,
    ManParm,
    ManParms,
    ManOption,
    SchedDef,
)

from flightanalysis.builders import elbuilders


@dataclass
class ManBuilder:
    mps: ManParms
    mpmaps: dict[str, dict]
    dgs: NamedTuple
    inter_criteria: NamedTuple
    box: TriangularBox | RectangularBox

    def create_eb(self, pe: PE) -> ElDef:
        el = getattr(self, pe.kind)(*pe.args, **pe.kwargs)
        if pe.centred:
            el.centred = True
        return el

    def _create_mdef(self, fig: Figure) -> ManDef:
        return self.create(
            fig.info,
            [self.create_eb(pe) if isinstance(pe, PE) else pe for pe in fig.elements],
            fig.relax_back,
            **fig.ndmps,
        )

    def create_mdef(self, fig: Figure | Option) -> ManDef | ManOption:
        try:
            if isinstance(fig, Option):
                return ManOption([self.create_mdef(op) for op in fig.figures])
            else:
                return self._create_mdef(fig)
        except Exception as ex:
            logger.error(ex)
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
                **(full_kwargs | {"Inter": self.inter_criteria}),
            )
            # neds = eds.add(eds)
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
            if isinstance(v, ManParm):  # add a new manparm
                mps.add(v)
            else:
                if k in mps.data:  # update the default value
                    mps[k].defaul = v
                else:  # create and add a manparm
                    if pd.api.types.is_list_like(v):
                        mps.add(
                            ManParm(
                                k, Combination("generated_combo", desired=v), 0, "rad"
                            )
                        )
                    else:
                        mps.add(ManParm.parse(v, mps, k))

        md = ManDef(
            ManInfo.model_validate(maninfo.model_dump()),
            mps,
            ElDefs(),
            replace(self.box, relax_back=relax_back),
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
                    logger.exception(ex)
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
        return md.update_dgs(self.dgs)

    @staticmethod
    def _parse_func(tomldata: dict):
        fun = getattr(elbuilders, tomldata["func"])
        args = getfullargspec(fun)[0]
        for arg in args:
            if arg=="Inter" or arg=="name":
                continue
            
            if arg not in tomldata["args"] and arg not in tomldata["kwargs"]:
                tomldata["kwargs"][arg] = None
        return dict(
            func=fun,
            args=tomldata["args"],
            kwargs=tomldata["kwargs"],
        )

    @staticmethod
    def parse_toml(file: Path, **kwargs) -> ManBuilder:
        toml = load(file.open("rb"))

        params = toml.get("parameters", {})

        for k, v in kwargs.items():
            if k in params:
                group = params[v]
                for param_name, param_value in group.items():
                    toml = replace_any_depth_value(toml, "parameters." + param_name, param_value)

        lookups = parse_expos_from_csv(Path.resolve(file.parent / toml["lookups"]))
        criteria = parse_criteria_csv(Path.resolve(file.parent / toml["criteria"]), lookups)
        intra_downgrades = parse_downgrade_csv(
            Path.resolve(file.parent / toml["intra_downgrades"]), criteria.intra
        )
        box_downgrades = parse_box_downgrades(
            Path.resolve(file.parent / toml["box_downgrades"]), criteria.box
        )
        box = parse_box(toml["box"], box_downgrades)
        mps = ManParms.parse_csv(Path.resolve(file.parent / toml["default_mps"]), criteria.inter)

        data = {
            k: ManBuilder._parse_func(v) for k, v in toml["builders"].items()
        }
        return ManBuilder(mps, data, intra_downgrades, criteria.inter, box)


def replace_any_depth_value(d: Any, old_value: Any, new_value: Any) -> dict:
    if pd.api.types.is_list_like(d):
        return [replace_any_depth_value(v, old_value, new_value) for v in d]
    elif isinstance(d, dict):
        return {k: replace_any_depth_value(v, old_value, new_value) for k, v in d.items()}
    elif d.__class__ is old_value.__class__ and d == old_value:
        return new_value
    else:
        return d
