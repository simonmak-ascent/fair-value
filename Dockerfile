FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir ".[mcp]"

EXPOSE 8000

CMD ["fair-value-mcp", "--http", "--host", "0.0.0.0", "--port", "8000"]
