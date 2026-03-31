# Architecture

Brahma's architecture is designed to provide a seamless full-stack experience by combining Python and Node.js.

## The Python-Node Bridge

At its core, Brahma uses a **Unix domain socket bridge** to communicate between the Python backend and the React frontend renderer.

1. **FastAPI Backend**: Acts as the primary server, handling routing, middleware, and business logic.
2. **Node.js Bridge (`unix_sock.js`)**: A lightweight Node.js process that listens on a Unix socket.
3. **Communication**: When an SSR request is needed, the Python server sends a JSON message containing the route and props to the Node.js bridge.
4. **Rendering**: Node.js imports the compiled React components and uses `react-dom/server` to generate the HTML stream.
5. **Response**: The HTML is streamed back through the socket and served by FastAPI.

## Internal Build Flow

Brahma's build process (`render_relay build`) consists of several steps:
1. **OpenAPI Generation**: The FastAPI app is inspected to generate an `openapi.json` file.
2. **TS Client Generation**: An NPM script uses the OpenAPI schema to generate a type-safe TypeScript client.
3. **Vite Build**: Vite compiles the React code, styles, and assets into the `_gingerjs/build` directory.

## File-System Integration

Brahma's `RouteProcessor` recursively scans the `src/app` directory to automatically register FastAPI routes for APIs, WebSockets, and UI Views.
