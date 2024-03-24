from flightanalysis import ScheduleAnalysis
from loguru import logger
import sys

logger.enable('flightanalysis')
logger.remove()
logger.add(sys.stdout, level="INFO")

analysis = ScheduleAnalysis.from_fcj("examples/data/manual_F3A_P23_22_05_31_00000350.json").run_all()

logger.info(f'Manoeuvre Downgrades:\n{analysis.summarydf()}')

total = sum([ma.scores.score() * ma.mdef.info.k for ma in analysis])
logger.info(f'Total score: {total}')