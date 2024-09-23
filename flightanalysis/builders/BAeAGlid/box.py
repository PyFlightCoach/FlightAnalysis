from flightanalysis.scoring.box import RectangularBox
from flightanalysis.builders.BAeAGlid.criteria import Glider
from flightanalysis.scoring.box import BoxDG


box = RectangularBox(
    width=1000,
    height=1000,
    depth=1000,
    distance=200,
    floor=100,
    bound_dgs=dict(
        bottom=BoxDG(Glider.intra.btmbox, "m"),
        **{
            direc: BoxDG(Glider.intra.box, "m")
            for direc in ["top", "left", "right", "front", "back"]
        }
    ),
)
