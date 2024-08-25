import logging
import sys


def create_logger():
    """
    Setups logger configuration.
    """
    logger = logging.getLogger('main_logger')
    logging_handler = logging.StreamHandler(sys.stdout)
    logging_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(logging_handler)
    logger.setLevel(logging.DEBUG)
    return logger


logger = create_logger()