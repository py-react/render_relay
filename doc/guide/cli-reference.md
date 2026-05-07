# CLI Reference

The `render_relay` command-line tool is the primary way to interact with Brahma.

## Commands

### `create-app`
Scaffolds a new Brahma project in the current directory.
```bash
render_relay create-app
```
Starts an interactive prompt to configure your project.

### `runserver`
Starts the Brahma development or production server.
```bash
# Development mode (with hot-reloading)
render_relay runserver dev

# Production mode
render_relay runserver
```

### `build`
Orchestrates the full production build process.
```bash
render_relay build
```
This command:
1. Generates the OpenAPI schema.
2. Creates the TypeScript API client.
3. Compiles the React frontend via Vite.

## Environment Variables

Brahma respects various environment variables that can also be set in `settings.py`:
- `DEBUG`: Enables development features and detailed error logs.
- `PORT`: The port the server listens on (default: 5001).
- `HOST`: The host interface to bind to (default: 0.0.0.0).
- `STATIC_SITE`: Toggles between SSR and SSG modes.
