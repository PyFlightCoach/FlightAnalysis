from dataclasses import dataclass
from flightdata import State
from flightanalysis.manoeuvre import Manoeuvre


@dataclass
class DGApplicator:
    man: Manoeuvre
    template: State

    def el(self, id: int):
        return self.man.elements[id]
    
    def tp(self, id: int):
        return self.template.get_element(id)

    def __call__(self, elid):
        raise NotImplementedError("This is an abstract class")