from flightanalysis.scoring.box import RectangularBox
from flightanalysis.builders.IAC.criteria import IAC
from flightanalysis.scoring.box import BoxDG

def make_iac_box(btm: float, top):
    return RectangularBox(
        width=1000,
        height=top-btm,
        depth=1000,
        distance=200,
        floor=btm,
        bound_dgs=dict(
            bottom=BoxDG(IAC.intra.btmbox, "m"),
            **{
                direc: BoxDG(IAC.intra.box, "m")
                for direc in ["top", "left", "right", "front", "back"]
            }
        ),
    )


unlimited_box = make_iac_box(100, 1100)
advanced_box = make_iac_box(200, 1100)
intermediate_box = make_iac_box(400, 1066)
sportsman_box = make_iac_box(600, 1066)