from flightdata.base.collection import Collection
from .criteria import Criteria



class CriteriaGroup(Collection):
    VType: Criteria = Criteria
    uid: str = "name"
