from __future__ import annotations
from flightanalysis import ManDef
from typing import NamedTuple
import pandas as pd


class ElName(NamedTuple):
    builder_id: int
    entity: int | None = None
    extra: str | None = None

    @staticmethod
    def parse(name: str) -> ElName:
        if name == "entry_line":
            return ElName(builder_id="entry")
        elif name == "exit_line":
            return ElName(builder_id="exit")
        vals = name.split("_")
        return ElName(*vals[1:])


def builder_df(mdef: ManDef):
    _ndf = pd.DataFrame({n: ElName.parse(n) for n in mdef.eds.keys()}).T
    _ndf.columns = ["builder_id", "entity", "extra"]
    _ndf = _ndf.assign(kind = [ed.Kind.__name__ for ed in mdef.eds])
    return _ndf

def builder_names(bdf: pd.DataFrame) -> dict[str, str]:
    bname_lookup = {}
    entity_counts = {eln: 0 for eln in bdf.kind.unique()}
    for _bid in bdf.builder_id.unique():
        _bdf = bdf.loc[bdf.builder_id == _bid]
        _kind = _bdf.kind.iloc[0]
        if _bid=="entry" or _bid=="exit":
            bname_lookup[_bid] = f"{_bid.capitalize()} {_kind}"
            continue
        entity_counts[_kind] += 1
        bname_lookup[_bid] = f"{_kind}{entity_counts[_kind]}"
    return bname_lookup

def _describe_eds(mdef: ManDef, bdf: pd.DataFrame, bnames: dict[str, str], add_exit: bool=False, latex_math: bool=False) -> dict[str, str]:
    new_names = []
    
    for k, v in bnames.items():
        _bdf = bdf.loc[bdf.builder_id == k]
        
        if len(_bdf) == 1:
            new_names.append(v)
        else:
            
            for i, (_, row) in enumerate(_bdf.iterrows()):
                _description = ""
                if row.extra and row.entity:
                    _description = f"{row.extra}{row.entity}"
                elif row.entity.startswith("pad"):
                    _description = row.entity
                elif row.extra is None:
                    _k = dict(
                        Line= "roll",
                        Snap= "snap",
                        Loop= "roll"
                    )
                    _description = f"{_k[row.kind]}{row.entity}"

                
                if latex_math:
                    _description = f"{{{_description}}}"
                new_names.append(f"{v}_{_description}")
    odict =  {ed.name: new_name for ed, new_name in zip(mdef.eds, new_names)}
    if add_exit:
        odict["exit_line"] = "Exit Line"
    return odict

def describe_eds(mdef: ManDef, add_exit: bool=False, latex_math: bool=False) -> list[str]:
    bdf = builder_df(mdef)

    return _describe_eds(mdef, bdf, builder_names(bdf), add_exit, latex_math)


def _describe_mps(mdef: ManDef, bnames: dict[str, str], latex_math: bool=False) -> dict[str, str]:
    mp_map = {}
    for mp in mdef.mps:
        for old_name, new_name in bnames.items():    
            if mp.name.startswith(f"e_{old_name}"):
                mp_map[mp.name] = mp.name.replace(f"e_{old_name}", new_name)
                break
        else:
            mp_map[mp.name] = mp.name
        if latex_math:
            _vals = mp_map[mp.name].split("_")
            if len(_vals) > 1:
                mp_map[mp.name] = f"{_vals[0]}_{{{'_'.join(_vals[1:])}}}"

    return mp_map

def describe_mps(mdef: ManDef, latex_math: bool=False) -> dict[str, str]:
    bdf = builder_df(mdef)
    bnames = builder_names(bdf)
    return _describe_mps(mdef, bnames, latex_math)


class MdefDescription(NamedTuple):
    eds: dict[str, str]
    mps: dict[str, str]

def describe_mdef(mdef: ManDef, latex_math: bool=False) -> MdefDescription:
    bdf = builder_df(mdef)
    bnames = builder_names(bdf)
    ed_map = _describe_eds(mdef, bdf, bnames, True, latex_math)
    mp_map = _describe_mps(mdef, bnames, latex_math)
    return MdefDescription(eds=ed_map, mps=mp_map)