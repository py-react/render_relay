FROM python:3.11-alpine AS builder

WORKDIR /app

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
COPY readme.md .
COPY MANIFEST.in .
COPY src/ ./src/

RUN pip install --no-cache-dir build .
RUN python -m build --no-isolation

FROM python:3.11-alpine

RUN pip install --no-cache-dir twine

COPY --from=builder /app/dist ./dist