# State Management

Brahma allows you to manage state across the Python-React boundary using several patterns.

## Server-to-Client State

Data fetched in Python's `index.py` is passed as props to your React component. This is the primary way to manage "server state."

```python
# index.py
async def index(request):
    return {"initialData": "Hello from Python"}
```

```jsx
// index.jsx
function Page({ initialData }) {
  const [data, setData] = useState(initialData);
  // ...
}
```

## Client-Side State

For pure UI state, use standard React hooks (`useState`, `useReducer`, `useContext`) or external libraries like Redux or Zustand.

## Shared Context

You can use the `getAppContext` hook in your root `layout.jsx` to wrap your entire application in a React Context provider, enabling global state management across all routes.

```jsx
// layout.jsx
import { MyProvider } from './context';

export default function Layout() {
  return (
    <MyProvider>
      <Outlet />
    </MyProvider>
  );
}
```

## Real-Time State

For real-time updates from Python to React, use **WebSockets**. Brahma's integrated WebSocket support allows for efficient, bidirectional state syncing without page reloads.
