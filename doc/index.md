---
layout: home

hero:
  name: Brahma
  text: Python meets React
  tagline: "The Foundational Engine for Full-Stack Performance. High-performance Python backends seamlessly integrated with modern React frontends."
  image:
    light: /static/brahma_logo_light.svg
    dark: /static/brahma_logo_dark.svg
    alt: Brahma Logo
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: Core Concepts
      link: /guide/what-is-brahma

features:
  - title: High-Performance Infrastructure
    details: Brahma leverages a specialized Unix Domain Socket Bridge to orchestrate high-speed SSR between Python and Node.js.
  - title: Unified Integration
    details: Seamlessly bridge the gap between your Python logic and React UI. Data flows between server and client with zero friction.
  - title: Efficient Routing
    details: Intelligent file-system based routing. Automatically map your directory structure to the web with zero-config simplicity.
  - title: Industrial-Grade DX
    details: Build with confidence using auto-generated, type-safe clients that keep your frontend and backend in perfect synchronization.
---

<div class="code-preview-section">

## The Integration Flow

<div class="code-grid">

<div class="code-card">

**1. Data Definition (Python)**

```python
# src/app/index.py
async def index(request):
    data = await db.fetch_user()
    return {"user": data}
```

</div>

<div class="code-card">

**2. Surface Presentation (React)**

```jsx
// src/app/index.jsx
export default function Page({ user }) {
  return <div>Welcome, {user.name}</div>
}
```

</div>

</div>

Brahma bridges the gap between the two environments, handling SSR, state hydration, and routing automatically.

</div>

<div class="why-brahma">

## Engineering Philosophy

In modern web development, teams often struggle to balance the ecosystem richness of Python with the interactivity of React. Brahma eliminates this trade-off. By implementing a high-performance **Unix Domain Socket Bridge**, it allows Python to act as the primary orchestrator, delivering fully rendered React experiences with minimal overhead and industry-leading latency.

</div>
