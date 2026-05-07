# Custom Error Pages

Brahma allows you to customize the error pages served to your users for various HTTP exceptions.

## Exception Templates

Brahma looks for HTML templates in the `public/templates` directory of your project. You can override the following default templates:

- `404.html`: Served when a route is not found.
- `500.html`: Served when an internal server error occurs.
- `bad_request.html`: Served for 400 Bad Request errors.

## Content Injection

Brahma uses Jinja2 for template rendering. You can use standard Jinja2 syntax to display error details if needed.

```html
<!-- public/templates/404.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found</title>
</head>
<body>
    <h1>Oops!</h1>
    <p>We couldn't find the page you were looking for.</p>
</body>
</html>
```

## Debug Mode

When `DEBUG = True` is set in `settings.py`, Brahma will serve detailed exception information instead of the custom templates to help you troubleshoot issues during development.
