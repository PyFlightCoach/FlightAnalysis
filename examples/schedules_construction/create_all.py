from .p23 import p23_def
from .a25 import a25_def
from .p25 import p25_def
from .f25 import f25_def
from .imac_unlimited_2024 import sdef as imac_unl2024_def
from .f3auk_clubman import clubman_def as f3auk_club_def
from .f3auk_Intermediate import intermediate_def as f3auk_int_def

sdefs = {
    'p23_schedule': p23_def, 
    'a25_schedule': a25_def, 
    'p25_schedule': p25_def, 
    'f25_schedule': f25_def, 
    'IMAC_Unlimited2024_schedule': imac_unl2024_def, 
    'f3auk_clubman_schedule': f3auk_club_def, 
    'f3auk_inter_schedule': f3auk_int_def
}


for sdef in sdefs:
    sdef.to_json("flightanalysis/data/p23_schedule.json")