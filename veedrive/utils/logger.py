import logging

from .. import config

logger = logging.getLogger()
logger.setLevel(config.LOG_LEVEL)
formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] - %(filename)s.%(funcName)s(%(lineno)d) - %(message)s",
)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
