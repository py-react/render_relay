# RenderRelay Production Blog Template

This is a production-ready, scalable blog architecture built on the RenderRelay framework.

## Architecture
- **Backend**: Service/Repository pattern with Pydantic schemas.
- **Frontend**: Tailwind CSS, React components for lists/details.
- **Caching**: Redis-based caching for high-performance reading.
- **Database**: Relational PostgreSQL schema.
- **Infrastructure**: Fully containerized with Docker and Docker Compose.

## Getting Started

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   ```

2. **Spin up Infrastructure**:
   ```bash
   docker-compose up -d
   ```

3. **Seed the Database**:
   ```bash
   docker-compose exec app python scripts/seed.py
   ```

4. **Launch Development Server**:
   ```bash
   npm run dev
   ```

## Key Features
- **Dynamic Routing**: Pure directory-based routing using RenderRelay's `index.py`/`index.jsx` pattern.
- **Premium UI**: Dark-mode optimized, responsive layout with high-end typography.
- **SEO & Performance**: SSR by default via RenderRelay's native Python-Node bridge.
- **Scale-Ready**: Decoupled service layer makes it easy to add new features or switch databases.

