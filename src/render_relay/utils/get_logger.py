import logging


def get_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        f"%(asctime)s [%(process)d] %(levelname)s {name}: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    return logger