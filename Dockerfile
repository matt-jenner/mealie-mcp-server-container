FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    MEALIE_MCP_SRC=/app/src \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    MCP_PATH=/mcp

WORKDIR /app

COPY pyproject.toml README.md UPSTREAM_LICENSE /app/
RUN uv sync --no-dev
COPY src /app/src
COPY remote_server.py /app/remote_server.py

EXPOSE 8000

CMD ["uv", "run", "python", "/app/remote_server.py"]
