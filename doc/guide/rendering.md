# Rendering

Brahma provides a sophisticated rendering engine that combines Python's server-side capabilities with React's client-side interactivity.

## Server-Side Rendering (SSR)

By default, Brahma performs SSR for all view routes. When a request hits the FastAPI server:
1. Python processes any server-side logic (see [Data Fetching](./data-fetching)).
2. The request is passed to a Node.js bridge via a Unix socket.
3. Node.js renders the React component to a stream using `renderToPipeableStream`.
4. The resulting HTML is piped back to the client.

## getAppContext

You can customize the rendering context by exporting a `getAppContext` function in your root `layout.jsx`. This is useful for integrating libraries like `styled-components`.

```jsx
import { ServerStyleSheet } from 'styled-components';

export const getAppContext = async (ctx) => {
  const sheet = new ServerStyleSheet();
  ctx.renderApp = () => ({
    enhanceApp: (App) => App,
    getStyles: (App) => sheet.collectStyles(App),
    styles: () => sheet.getStyleTags(),
    finally: () => {
      sheet.seal()
    }
  })
  return ctx
}
```

## Static Site Generation (SSG)

Brahma also supports static rendering. When `STATIC_SITE` is enabled in your `settings.py`, Brahma can pre-render your pages at build time.
