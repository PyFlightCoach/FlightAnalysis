import numpy as np
from flightanalysis.scoring.box import TriangularBox


box = TriangularBox(
    width=np.radians(120),
    height=np.radians(60),
    depth=25,
    distance=150,
    floor=np.radians(15),
    bound_dgs=dict(),
)
