from flightanalysis.definition.maninfo.positioning import Heading
import numpy as np

def test_heading_infer():
    tbs = [
        [Heading.RIGHT, np.radians(10)],
        [Heading.RIGHT, np.radians(-10)],
        [Heading.RIGHT, np.radians(350)],
        [Heading.RIGHT, np.radians(370)],
        [Heading.LEFT, np.radians(180)],
        [Heading.LEFT, np.radians(-182)],
        [Heading.LEFT, np.radians(182)],
    ]


    for tb in tbs:
        assert tb[0] == Heading.infer(tb[1])
