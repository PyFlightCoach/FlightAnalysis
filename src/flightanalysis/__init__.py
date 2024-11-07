from .version import __version__  # noqa: F401
from .elements import *  # noqa: F403
from .manoeuvre import Manoeuvre  # noqa: F401
from .schedule import Schedule  # noqa: F401
from .definition import *  # noqa: F403
from .scoring import *  # noqa: F403
from .analysis import ScheduleAnalysis, ElementAnalysis, manoeuvre_analysis as ma  # noqa: F401

import sys
from loguru import logger

logger.disable('flightanalysis')

def enable_logging(level: str = 'INFO'):
    logger.enable('flightanalysis')
    logger.remove()
    logger.add(
        sys.stderr,
        level=level
    )
    return logger

