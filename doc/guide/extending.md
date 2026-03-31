# Extending the App

Brahma is built on top of FastAPI, which means you have full access to its ecosystem and can extend the underlying application instance as needed.

## The extend_app Hook

Create an `extend_app` function in your project's `main.py` (or the location specified by your entry point) to gain access to the `FastAPI` app instance.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def extend_app(app: FastAPI):
    # 1. Add custom routes
    @app.get("/health-check")
    async def health_check():
        return {"status": "ok"}

    # 2. Add custom Exception Handlers
    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={"message": "This is a custom JSON 404 response"},
        )

    # 3. Mount existing FastAPI sub-apps
    # app.mount("/api/v2", subapi)
```

## Why Extend the App?

Extending the app is useful for:
- Integrating with databases (e.g., SQLAlchemy, Tortoise).
- Adding background tasks.
- Implementing custom authentication schemes.
- Mounting external APIs or microservices within the same process.
