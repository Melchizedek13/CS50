import logging
import sys

LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s: %(levelname)s: %(message)s'


def get_logger():
    logging.basicConfig(
        format=LOGGING_FORMAT,
        level=LOGGING_LEVEL,
        handlers=[logging.StreamHandler(sys.stdout)])

    logger = logging.getLogger()
    return logger
