
from dataclasses import dataclass



@dataclass
class DynamicDownGrade:
    """Pre calculated optimisation space for a downgrade to facilitate faster segmentation optimisation."""
    dg_name: str

