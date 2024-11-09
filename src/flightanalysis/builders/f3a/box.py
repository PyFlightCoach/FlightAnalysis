from flightanalysis.scoring.box import TriangularBox
from flightanalysis.builders.f3a.criteria import F3A
from flightanalysis.scoring.box import BoxDG
import numpy as np


box = TriangularBox(
    width = np.radians(120),
    height = np.radians(60),
    depth = 25,
    distance = 150,
    floor = np.radians(15),
    bound_dgs=dict(
        top=BoxDG(F3A.intra.box, 'rad'),
        right=BoxDG(F3A.intra.box, 'rad'),
        left=BoxDG(F3A.intra.box, 'rad'),
        back=BoxDG(F3A.intra.depth, 'm')
    ),
    centre_criteria=F3A.intra.angle
)


