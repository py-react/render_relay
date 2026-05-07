import inspect
from functools import wraps
from starlette.concurrency import run_in_threadpool

def api(module):
    @wraps(module)
    async def api_func(*args, **kwargs):
        if inspect.iscoroutinefunction(module):
            return await module(*args, **kwargs)
        else:
            return await run_in_threadpool(module, *args, **kwargs)
    return api_func