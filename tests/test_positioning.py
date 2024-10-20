from flightanalysis.definition.maninfo.positioning import Heading
import numpy as np

def test_heading_infer():
    tbs = [
        [Heading.LTOR, np.radians(10)],
        [Heading.LTOR, np.radians(-10)],
        [Heading.LTOR, np.radians(350)],
        [Heading.LTOR, np.radians(370)],
        [Heading.RTOL, np.radians(180)],
        [Heading.RTOL, np.radians(-182)],
        [Heading.RTOL, np.radians(182)],
    ]


    for tb in tbs:
        assert tb[0] == Heading.infer(tb[1])
