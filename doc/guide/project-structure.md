# Project Structure

A typical Brahma project follows a specific directory structure designed to keep your Python and React code organized and well-integrated.

## Top-Level Folders

- **`src/app/`**: The heart of your application. All file-system based routes (API and View) are defined here.
- **`src/components/`**: Reusable React components that aren't tied to a specific route.
- **`src/libs/`**: Shared libraries, hooks, and utilities.
- **`public/`**: Static assets that are served directly.
  - **`static/`**: Images, fonts, and other files.
  - **`templates/`**: Custom HTML templates for layout and error pages.
- **`_gingerjs/`**: (Auto-generated) Contains the compiled build and the Node.js SSR runtime logic. **Do not modify.**

## Key Files

- **`settings.py`**: Global Python configuration (Port, Debug mode, etc.).
- **`package.json`**: Manages JavaScript dependencies and build scripts.
- **`pyproject.toml`**: Python package configuration and dependencies.
- **`ginger_conf.cjs`**: Optional overrides for Vite and internal build settings.
- **`main.py`**: The entry point for extending the FastAPI application instance.

## Route-Level Files

Inside `src/app/`, you'll find:
- **`index.jsx`**: Defies the UI for a route.
- **`index.py`**: The unified Python file for a route. It can contain `index` (page props or WebSocket), `layout` (layout props), `middleware`, and `meta_data`.
- **`layout.jsx`**: Defines a shared layout for a directory and its sub-directories.
- **`loading.jsx`**: (Optional) Defines a loading state for the route.
