from flightanalysis import ScheduleAnalysis
from loguru import logger
import sys
from json import dump

logger.enable('flightanalysis')
logger.remove()
logger.add(sys.stdout, level="INFO")

analysis = ScheduleAnalysis.from_fcj("examples/data/manual_F3A_P23_22_05_31_00000350.json").run_all()

for ma in analysis:
    dump(ma.to_dict(), open(f"examples/scoring/manoeuvres/mans/{ma.name}.json", 'w'))