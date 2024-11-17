from flightanalysis.definition.mandef import ManDef

class ManOption:
    def __init__(self, options: list[ManDef], active=0) -> None:
        assert all(o.uid==options[0].uid for o in options), 'all options must have the same short name'
        self.options = options
        self.active=active
    
    def __repr__(self) -> str:
        return f'ManOption({[md.info.name for md in self.options]})'

    @property
    def uid(self):
        return self.options[0].uid
    
    def to_dict(self):
        return [o.to_dict() for o in self.options]
    
    @staticmethod
    def from_dict(data:list[dict]):
        return ManOption([ManDef.from_dict(d) for d in data])
    
    def __getitem__(self, i):
        return self.options[i]
    
    @property
    def info(self):
        return self[self.active].info
    
    @property
    def mps(self):
        return self[self.active].mps
    
    @property
    def eds(self):
        return self[self.active].eds
    
    def __iter__(self):
        for mdef in self.options:
            yield mdef