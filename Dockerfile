FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ARG MEALIE_MCP_REPO=https://github.com/rldiao/mealie-mcp-server
ARG MEALIE_MCP_REF=f7a2a5e21e68e223629393a5ad16f55dca6ea577

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    MEALIE_MCP_SRC=/app/mealie-mcp-server/src \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    MCP_PATH=/mcp

WORKDIR /app

COPY scripts/fetch_upstream.py /app/fetch_upstream.py
RUN python /app/fetch_upstream.py "$MEALIE_MCP_REPO" "$MEALIE_MCP_REF" /app/mealie-mcp-server

WORKDIR /app/mealie-mcp-server

RUN uv sync --frozen --no-dev

COPY remote_server.py /app/remote_server.py

EXPOSE 8000

CMD ["uv", "run", "python", "/app/remote_server.py"]
