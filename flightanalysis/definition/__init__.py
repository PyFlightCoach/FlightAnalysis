
from numbers import Number

from .operations import *
from .maninfo import ManInfo, BoxLocation, Orientation, Direction, Height, Position
from .collectors import Collector, Collectors

from .manparm import ManParm, ManParms, DummyMPs

def _a(arg):
    if isinstance(arg, ManParm):
        return arg.valuefunc()
    elif isinstance(arg, Number):
        return lambda mps: arg
    elif isinstance(arg, Opp):
        return arg
    

from .eldef import ElDef, ElDefs
from .mandef import ManDef
from .scheddef import SchedDef, ScheduleInfo
from .builders.manbuilder import ManBuilder, f3amb, MBTags, centred, imacmb, r, c45, dp
