from pfcschemas import ManInfo
from typing import Callable
from flightanalysis.definition import SchedDef, ManOption, ManDef, ElDef
from flightanalysis.builders.manbuilder import ManBuilder, centred as centre


class ElBuilder:
    def __init__(self, name):
        self.name = name
        self.centred=False

    def __call__(self, *args, **kwargs) -> Callable[[ManBuilder], list[ElDef]]:
        if self.centred:
            em = lambda mb: centre(getattr(mb, self.name)(*args, **kwargs))
        else:
            em = lambda mb: getattr(mb, self.name)(*args, **kwargs)
        return em
    
    def __repr__(self):
        return f"{self.name}()"
        

loop = ElBuilder("loop")
line = ElBuilder("line")
roll = ElBuilder("roll")
stallturn = ElBuilder("stallturn")
spin = ElBuilder("spin")
snap = ElBuilder("snap")

def centred(elb: ElBuilder) -> ElBuilder:
    elb.centred = True
    return elb


def manoeuvre(
    maninfo: ManInfo,
    elbuilders: list[ElBuilder | int],
    relax_back=False,
    **kwargs,
) -> Callable[[ManBuilder], ManDef | ManOption]:
    return lambda mb: mb.create(
        maninfo,
        [eb(mb) if isinstance(eb, Callable) else eb for eb in elbuilders],
        relax_back,
        **kwargs,
    )


def schedule(
    makers: list[Callable[[ManBuilder], ManDef | ManOption]],
) -> Callable[[ManBuilder], SchedDef]:
    return lambda mb: SchedDef([m(mb) for m in makers])
