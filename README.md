# Mealie MCP Server Container

Docker wrapper for [`rldiao/mealie-mcp-server`](https://github.com/rldiao/mealie-mcp-server). It packages the upstream Python MCP server and exposes it as a remote MCP service over internal HTTP using FastMCP `streamable-http` transport.

This repository does not reimplement Mealie MCP tools. The container build fetches a pinned upstream source archive from `rldiao/mealie-mcp-server`, and this repository supplies the container, remote HTTP wrapper, deployment examples, and tests.

## Security Model

The container holds a Mealie API key in its runtime environment. Remote MCP users do not authenticate to this container, so anyone who can reach the MCP endpoint can use the Mealie permissions granted by that API key.

Use network controls as the primary defense:

- HTTPS reverse proxy access rules
- firewall rules
- VPN or private network access
- Docker network isolation
- proxy-level IP allowlists

`MCP_ALLOWED_SUBNETS` provides an optional second-level in-container allowlist. It checks the direct peer IP only and does not trust `X-Forwarded-For` by default. Behind a reverse proxy, the direct peer is usually the proxy container or host, so the allowlist normally needs to include the proxy's Docker subnet or proxy IP.

## Runtime Configuration

Copy `.env.example` to `.env` for local use and set real values. Do not commit `.env`.

Required:

- `MEALIE_BASE_URL`: base URL for your Mealie instance, for example `http://mealie:9000`
- `MEALIE_API_KEY`: Mealie API key used by the MCP server

For production, prefer your orchestrator or secret manager for `MEALIE_API_KEY` when available. Examples include Kubernetes secrets, systemd environment files with restricted permissions, or Docker/Podman secrets surfaced as environment variables by your deployment tooling. `.env` is convenient for local testing but should remain local-only.

Optional:

- `MCP_HOST`: bind host, default `0.0.0.0`
- `MCP_PORT`: bind port, default `8000`
- `MCP_PATH`: MCP endpoint path, default `/mcp`
- `MCP_ALLOWED_SUBNETS`: comma-separated CIDRs; empty means allow all direct peers
- `LOG_LEVEL`: default `INFO`

## Build

Run from this repository root:

```bash
docker build -t mealie-mcp-server-container .
```

Podman equivalent:

```bash
podman build -t mealie-mcp-server-container .
```

By default the Dockerfile downloads `https://github.com/rldiao/mealie-mcp-server/archive/f7a2a5e21e68e223629393a5ad16f55dca6ea577.tar.gz` and installs dependencies using the upstream `uv.lock` with `uv sync --frozen --no-dev`.

To intentionally build a newer upstream commit or tag, override `MEALIE_MCP_REF`:

```bash
docker build --build-arg MEALIE_MCP_REF=<commit-or-tag> -t mealie-mcp-server-container .
```

Keep secrets such as `.env` files out of the build context, especially when using remote builders. The repository `.dockerignore` excludes common local secret and cache files.

## Run Locally

From this repository root:

```bash
cp .env.example .env
```

Edit `.env`, then run:

```bash
docker run --rm -p 8000:8000 --env-file .env mealie-mcp-server-container
```

This publishes port `8000` on the host. Use it only for local testing or behind appropriate firewall/private-network controls; do not expose it publicly without access restrictions.

Podman equivalent:

```bash
podman run --rm -p 8000:8000 --env-file .env mealie-mcp-server-container
```

Internal MCP endpoint:

```text
http://localhost:8000/mcp
```

If Mealie runs on the Docker host rather than a Docker network, use a host-gateway mapping and set `MEALIE_BASE_URL` to `http://host.docker.internal:<port>`:

```bash
docker run --rm -p 8000:8000 --add-host=host.docker.internal:host-gateway --env-file .env mealie-mcp-server-container
```

Podman may require host networking or an explicit host alias depending on your setup.

## Published Image

Images are published to GitHub Container Registry on pushes to `main`:

```bash
docker pull ghcr.io/matt-jenner/mealie-mcp-server-container:latest
```

Run the published image:

```bash
docker run --rm -p 8000:8000 \
  -e MEALIE_BASE_URL=http://mealie:9000 \
  -e MEALIE_API_KEY=your-api-key \
  ghcr.io/matt-jenner/mealie-mcp-server-container:latest
```

The workflow also publishes a short commit-SHA tag for each build.

## HTTPS Proxy Deployment

The container serves plain HTTP. Terminate HTTPS at your reverse proxy.

Typical internal upstream target:

```text
http://mealie-mcp-server:8000/mcp
```

Typical external MCP URL:

```text
https://your-domain.example/mcp
```

Websocket support is not the core requirement for `streamable-http`. Standard HTTP streaming/proxy buffering behavior matters more. If clients hang or responses buffer unexpectedly, disable proxy buffering for this route.

## Compose Example

`compose.yaml` shows how to attach this service to an existing Docker network used by Mealie and your proxy:

```bash
docker compose up --build
```

If you use Podman Compose, the equivalent is usually:

```bash
podman compose up --build
```

Update the external network name before use:

```yaml
networks:
  mealie_internal:
    external: true
```

## Validation

Build validation from this repository root:

```bash
docker build -t mealie-mcp-server-container .
```

Unit tests for wrapper-owned behavior from this project directory:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

Mock Mealie smoke test from this project directory:

```bash
docker compose -f compose.test.yaml up --build
```

Podman Compose equivalent:

```bash
podman compose -f compose.test.yaml up --build
```

If Compose support is unavailable, use a temporary Podman network from this repository root:

```bash
podman network create mealie-mcp-test
podman run -d --name mock-mealie --network mealie-mcp-test -v "$PWD/tests/mock_mealie.py:/mock_mealie.py:ro,z" python:3.12-slim python /mock_mealie.py
podman run -d --name mealie-mcp-smoke --network mealie-mcp-test -e MEALIE_BASE_URL=http://mock-mealie:9000 -e MEALIE_API_KEY=mock-api-key mealie-mcp-server-container
podman run --rm --network mealie-mcp-test -v "$PWD/scripts/list_tools_smoke.py:/list_tools_smoke.py:ro,z" mealie-mcp-server-container uv run python /list_tools_smoke.py http://mealie-mcp-smoke:8000/mcp
podman rm -f mock-mealie mealie-mcp-smoke
podman network rm mealie-mcp-test
```

Then, in another shell, verify the MCP server can initialize and list tools:

```bash
python scripts/list_tools_smoke.py http://localhost:8000/mcp
```

The smoke script initializes the MCP session, lists tools, and fails if these expected tool names are missing:

- `get_recipes`
- `get_shopping_lists`
- `get_categories`

Real Mealie validation should start with read-only operations. Run write tests only against disposable data or a non-production Mealie instance.

## File Uploads

The upstream MCP server includes tools that upload recipe images or assets from local file paths. In a containerized deployment, those paths must exist inside the container. Bind mount any upload directory read-only, for example:

```bash
docker run --rm -p 8000:8000 --env-file .env -v /host/mealie-files:/mnt/mealie-files:ro mealie-mcp-server-container
```
