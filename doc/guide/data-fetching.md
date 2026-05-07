# Data Fetching

Brahma makes it easy to fetch data in Python and pass it directly to your React components.

## Server-Side Props

The primary way to fetch data is by creating an `index.py` file alongside your `index.jsx` (or in a directory for `layout.jsx`). All server-side logic for a route directory resides in its `index.py`.

### Convention

Export an `async` function named `index` for page data, or `layout` for layout data, in your `index.py`.

**src/app/products/index.py**
```python
from fastapi import Request
import requests

async def index(request: Request):
    response = requests.get('https://api.example.com/products')
    data = response.json()
    return {"products": data}
```

**src/app/products/index.jsx**
```jsx
function ProductsPage({ products }) {
  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  );
}

export default ProductsPage;
```

## Type-Safe Client

Brahma automatically generates a TypeScript client based on your FastAPI backend. You can import `DefaultService` to make type-safe API calls from your client-side components.

```js
import { DefaultService } from "@/gingerJs_api_client";

const data = await DefaultService.getProducts();
```
