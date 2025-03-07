import logging

__version__ = "2.2.1"

from pybinsim2.application import BinSim


def init_logging(loglevel):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)

    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("pybinsim2")
    logger.addHandler(console_handler)
    logger.setLevel(loglevel)

    return logger


logger = init_logging(logging.INFO)
logger.info("Starting pybinsim2 v{}".format(__version__))
