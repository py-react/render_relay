# Routing

Brahma uses a file-system based router, where the directory structure of your `src/app` folder defines the routes of your application.

## View Routes

Any `index.jsx` (or `.tsx`) file within the `src/app` directory becomes a route.

- `src/app/index.jsx` → `/`
- `src/app/about/index.jsx` → `/about`
- `src/app/dashboard/settings/index.jsx` → `/dashboard/settings`

## Layouts

Layouts are shared UI components that wrap multiple pages. Define a layout by creating a `layout.jsx` file in a directory.

```jsx
import React from "react";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div className="layout-container">
      <nav>My Navbar</nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
```

Layouts nest automatically. A layout in `src/app/dashboard/layout.jsx` will wrap all routes under `/dashboard/*`.

## API Routes

API routes are defined in the `src/app/api` directory. Like views, they are controlled by `index.py` files.

- `src/app/api/hello/index.py` → `/api/hello`

Brahma supports standard HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, etc.) as exported functions in your `index.py`.

## Dynamic Segments

Create dynamic routes by wrapping a folder name in square brackets.

- `src/app/products/[id]/index.jsx` → `/products/:id`

You can access the dynamic parameters using the `useParams` hook from `react-router-dom`.
