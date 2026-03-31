# Meta Data

Brahma makes SEO management simple by allowing you to define meta tags directly in your Python logic.

## The meta_data Function

In any `index.py`, you can export an `async def meta_data()` function that returns a dictionary of meta tags.

### Example

**src/app/index.py**
```python
def meta_data():
    return {
        "title": "Brahma | The Python-React Framework",
        "description": "Experience the power of Python with the beauty of React.",
        "og:title": "Brahma Framework",
        "og:description": "FastAPI + React = Brahma",
        "og:image": "/static/images/og-image.png",
        "icon": "/static/images/favicon.ico"
    }
```

## Dynamic Meta Data

Since `meta_data` is a standard Python function, you can generate tags dynamically based on data or logic.

```python
def meta_data():
    project_name = "Brahma"
    return {
        "title": f"{project_name} - Documentation",
        "description": f"Learn how to build apps with {project_name}"
    }
```

## Fallbacks

If a child route does not define `meta_data`, Brahma will look for `meta_data` in parent layouts or fall back to the global defaults.
