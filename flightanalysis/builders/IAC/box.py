from flightanalysis.scoring.box import RectangularBox
from flightanalysis.builders.IAC.criteria import IAC
from flightanalysis.scoring.box import BoxDG


unlimited_box = RectangularBox(
    width=1000,
    height=1000,
    depth=1000,
    distance=200,
    floor=100,
    bound_dgs=dict(
        bottom=BoxDG(IAC.intra.btmbox, "m"),
        **{
            direc: BoxDG(IAC.intra.box, "m")
            for direc in ["top", "left", "right", "front", "back"]
        }
    ),
)
