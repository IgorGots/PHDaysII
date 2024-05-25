import logging
import sys

logging.getLogger('transitions').setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


APP_LOGGER_NAME = 'LLM'

def setup_applevel_logger(logger_name: str = APP_LOGGER_NAME, file_name: str = None) -> logging.Logger:

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s:%(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(sh)

    if file_name is not None:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    return logging.getLogger(APP_LOGGER_NAME).getChild(module_name)
