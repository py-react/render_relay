# WebSockets

Brahma provides first-class support for WebSockets, allowing you to build real-time interactive features easily.

## WebSocket Routes

WebSocket routes are defined in the `src/app/app-sockets` directory.

- `src/app/app-sockets/chat/index.py` → `ws://yourdomain.com/ws/chat`

Note: All WebSocket routes are automatically prefixed with `/ws`.

## Implementation

In your `index.py`, export an `async def index` function. This function receives the `WebSocket` object directly.

```python
from fastapi import WebSocket

async def index(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
```

## Client-Side Usage

You can use the standard browser `WebSocket` API or any React library to connect to your Brahma WebSocket endpoints.

```jsx
import React, { useEffect } from 'react';

function ChatComponent() {
  useEffect(() => {
    const socket = new WebSocket('ws://localhost:5001/ws/chat');
    
    socket.onmessage = (event) => {
      console.log('Received:', event.data);
    };

    return () => socket.close();
  }, []);

  return <div>Check console for real-time messages!</div>;
}
```
