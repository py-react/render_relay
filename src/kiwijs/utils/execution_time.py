import time
import functools
from kiwijs.utils.get_logger import get_logger
from kiwijs.utils.constant import level_map

def excecution_time(func):
    logger = get_logger("ExecutionTime")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper