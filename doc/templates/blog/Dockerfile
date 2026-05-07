FROM python:3.11-slim as backend

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RenderRelay uses a Unix Socket for Python-Node bridge
# Ensure the runtime env has necessary permissions
# RenderRelay uses a Unix Socket for Python-Node bridge
# Ensure the runtime env has necessary permissions
ENV DEBUG=false
ENV PYTHONUNBUFFERED=1

CMD ["render_relay", "runserver"]

