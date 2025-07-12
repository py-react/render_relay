import logging
from .load_settings import load_settings
from .constant import level_map

settings = load_settings()

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(level_map[settings.get("LOG_LEVEL","INFO")])
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        f"%(asctime)s [%(process)d] %(levelname)s {name}: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


