# Configuration & Settings

Brahma provides a flexible configuration system that allows you to manage environment variables, application settings, and build-time options.

## Application Settings

Brahma looks for a `settings.py` file in the root of your project. This file is used to define global configuration options.

### Default Settings

```python
# settings.py
DEBUG = True
PORT = 5001
HOST = "0.0.0.0"
PACKAGE_MANAGER = "npm" # or "yarn"
```

You can add any custom configuration here and access it via the `load_settings` utility within your Python logic.

## Environment Variables

Brahma automatically loads environment variables. You can use standard Python `os.environ` or external libraries like `python-dotenv` within your `settings.py` or `index.py` files.

## Vite Configuration

To override the default Vite configuration, create a `ginger_conf.cjs` file at the root of your project.

```javascript
// ginger_conf.cjs
module.exports = {
    vite: {
        // Custom Vite configuration options
        server: {
            proxy: {
                '/api': 'http://localhost:5000'
            }
        }
    }
}
```

This allows you to customize the build and development server behavior of the React frontend.
