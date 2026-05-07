# Static Site Generation (SSG)

Brahma supports Static Site Generation, allowing you to build your application into a self-contained set of static assets that can be hosted on any web server or static hosting provider (GitHub Pages, S3, Vercel, Netlify).

## Enabling SSG

To switch Brahma into static mode, set the `STATIC_SITE` flag to `True` in your `settings.py`.

```python
# settings.py
STATIC_SITE = True
```

## How it Works

When `STATIC_SITE` is enabled, Brahma significantly alters its build and routing behavior:

- **Entry Point**: The framework switches from `layout.html` (dynamic SSR) to `index.html` (static SPA).
- **Asset Paths**: Asset resolution is optimized for static hosting, using standard relative paths that don't depend on a running Python backend for serving.
- **Client-Side Routing**: The application relies on `react-router-dom` for handling all navigation within the browser.
- **Direct Hosting**: The resulting `_gingerjs/build/static` folder can be served directly by any web server without requiring a Python environment.

## The Build Process

Running `render_relay build` in SSG mode performs the following:

1. **Static Bundle**: Vite compiles your React components, CSS, and assets into a production-ready static bundle.
2. **Path Resolution**: The build tool ensures all internal links and imports are resolved correctly for static serving.
3. **Template Injection**: Static scripts and style tags are injected directly into the `index.html` file.

## Deployment

In SSG mode, you don't need to run `render_relay runserver` in production. Instead:

1. Run `render_relay build`.
2. Deploy the contents of the `_gingerjs/build/static` directory to your hosting provider.
3. Ensure your provider is configured to serve `index.html` for all unknown routes (Single Page Application configuration).

## Limitations

- **Server-Side Props**: Since there is no Python backend at request time, `index.py` server-side props will not be executed. You should use client-side data fetching (e.g., `useEffect` or React Query) instead.
- **Dynamic Meta Tags**: Meta tags defined in Python's `meta_data()` will not be dynamic per-request; they will be baked into the static bundle during the build phase.
