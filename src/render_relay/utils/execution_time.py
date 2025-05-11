import logging
import time
import functools

logger = logging.getLogger(__name__)

def excecution_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper