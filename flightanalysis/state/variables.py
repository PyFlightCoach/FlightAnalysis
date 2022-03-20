from flightanalysis.base import Constructs, SVar, default_vars
from flightanalysis.base import make_dt, make_error
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np





def make_bvel(sec) -> Points:
    wvel = sec.gpos.diff(sec.gdt)
    return sec.gatt.inverse().transform_point(wvel)

def make_brvel(sec) -> Points:
    return sec.gatt.body_diff(sec.gdt).remove_outliers(3) 

def make_bacc(sec) -> Points:
    wacc = sec.gatt.transform_point(sec.gbvel).diff(sec.gdt) + Point(0, 0, 9.81) # assumes world Z is up
    return sec.gatt.inverse().transform_point(wacc)

def make_bracc(sec) -> Points:
    return sec.gbrvel.diff(sec.gdt)


secvars = Constructs(dict(**default_vars, **{
    "pos":   SVar(["x", "y", "z"],          Point,      Points,      make_error),
    "att":   SVar(["rw", "rx", "ry", "rz"], Quaternion, Quaternions, make_error),
    "bvel":  SVar(["bvx", "bvy", "bvz"],    Point,      Points,      make_bvel),
    "brvel": SVar(["brvr", "brvp", "brvy"], Point,      Points,      make_brvel),
    "bacc":  SVar(["bax", "bay", "baz"],    Point,      Points,      make_bacc),
    "bracc": SVar(["brar","brap", "bray"],  Point,      Points,      make_bracc),
}))