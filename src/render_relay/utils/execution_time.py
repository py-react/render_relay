import time
import functools
from render_relay.utils.get_logger import get_logger
from render_relay.utils.constant import level_map

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