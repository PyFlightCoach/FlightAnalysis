from json import load
from flightanalysis import *
from flightdata import *

with open('examples/scoring/manual_F3A_F25_24_01_05_00000177_analysis.json') as f:
    f25 = load(f)
    

ma = ManoeuvreAnalysis.from_fcs_dict(f25['data']['sFin'])


ea = ma.e_0_rolls
dg = ea.el.intra_scoring.roll_angle
res = dg(ea.fl, ea.tp)

pass