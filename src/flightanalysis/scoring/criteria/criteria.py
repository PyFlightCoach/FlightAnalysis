from .exponential import Exponential, free
from dataclasses import dataclass, field


def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)])



@dataclass
class Criteria:
    lookup: Exponential = field(default_factory=lambda : free)

    def prepare(self, value):
        return value

    def to_dict(self):
        data = self.__dict__.copy()
        lookup = data.pop('lookup')
        return dict(
            kind=self.__class__.__name__,
            lookup=lookup.__dict__,
            **data
        )
    
    @staticmethod
    def from_dict(data: dict):
        if data is None:
            return None
        data = data.copy()
        name = data.pop('kind')
        
        for Crit in all_subclasses(Criteria):
            if Crit.__name__ == name:
                lookup = data.pop('lookup')
                if 'comparison' in data: 
                    data.pop('comparison')
                return Crit(lookup=Exponential(**lookup), **data)
        raise ValueError(f'cannot parse Criteria from {data}')
    
    def to_py(self):
        _so = f"{self.__class__.__name__}(Exponential({self.lookup.factor},{self.lookup.exponent}, {self.lookup.limit} )"
        if hasattr(self, 'min_bound'):
            _so = f"{_so}, min_bound={self.min_bound}"
        if hasattr(self, 'min_bound'):
            _so = f"{_so}, max_bound={self.max_bound}"
        if hasattr(self, 'limit'):
            _so = f"{_so}, limit={self.limit}"
        return _so + ')'
    
        
@dataclass
class CriteriaRes:
    pass