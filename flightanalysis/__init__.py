from loguru import logger
from .elements import *
from .manoeuvre import Manoeuvre
from .schedule import Schedule
from .definition import *
from .scoring import *
from .analysis import *
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")

def set_log_level(level: str):
    logger.remove()
    logger.add(sys.stderr, level=level)