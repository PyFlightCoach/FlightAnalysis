from flightanalysis import ManDef


class ManOption:
    def __init__(self, options: list[ManDef]) -> None:
        assert all(o.uid==options[0].uid for o in options), 'all options must have the same short name'
        self.options = options
    
    @property
    def uid(self):
        return self.options[0].uid
    
    def to_dict(self):
        return [o.to_dict() for o in self.options]
    
    @staticmethod
    def from_dict(data:list[dict]):
        return ManOption([ManDef.from_dict(d) for d in data])
    
    