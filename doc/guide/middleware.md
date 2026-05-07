# Middleware

Brahma leverages FastAPI's powerful middleware system, allowing you to intercept requests and responses at various levels.

## Global Middleware

You can add global middleware that runs for every request by extending the app instance in your `main.py`.

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

def extend_app(app: FastAPI):
    app.add_middleware(MyMiddleware)
```

## Route-Level Middleware

Brahma allows you to define middleware directly in your `index.py` files. This middleware will only apply to the route (and sub-routes) defined in that directory.

### Convention

Export an `async` function named `middleware` in your `index.py`.

**src/app/index.py**
```python
from fastapi import Request

async def middleware(request: Request, call_next):
    token = request.headers.get('X-Auth-Token')
    if token != 'secret-token':
        # You can raise an HTTPException here
        pass
    return await call_next(request)
```

## Middleware Execution Order

1. Global Middlewares (added via `add_middleware`).
2. Brahma Internal Middlewares.
3. Route-specific Middlewares (defined in `index.py`).
