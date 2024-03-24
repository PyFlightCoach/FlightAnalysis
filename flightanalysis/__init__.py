from loguru import logger
from .elements import *
from .manoeuvre import Manoeuvre
from .schedule import Schedule
from .definition import *
from .scoring import *
from .analysis import ScheduleAnalysis, ElementAnalysis
from .analysis import manoeuvre_analysis as ma

logger.disable('flightanalysis')
