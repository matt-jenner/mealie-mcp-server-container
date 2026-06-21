# Feature 02: Remote HTTP MCP Wrapper

## Goal

Expose the upstream Mealie MCP server as a remote MCP service over internal plain HTTP using FastMCP's `streamable-http` transport.

## Status

State: Complete

Stories:

- [x] Story 02.1: Import Upstream MCP App
- [x] Story 02.2: Serve Streamable HTTP
- [x] Story 02.3: Avoid Forking Upstream Runtime Logic

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Python syntax checks passed for wrapper, test, and smoke files.
- Missing required Mealie env vars fail startup with upstream `ValueError`.
- Podman no-compose mock Mealie MCP smoke test succeeded and listed expected tools.
- Docker is unavailable in this environment; Docker-specific commands were not validated separately from Podman.
- Reverse proxy route validation remains deployment-environment-specific/manual.

## Context

The upstream server currently runs stdio from `src/server.py` using `mcp.run(transport="stdio")`. The locked upstream dependency `mcp==1.12.0` supports `streamable-http` and exposes `mcp.streamable_http_app()`, allowing this wrapper to run the same registered tools over HTTP without rewriting tool logic.

## Stories

### Story 02.1: Import Upstream MCP App

As the maintainer, I want the wrapper to import the upstream `mcp` object so all upstream tools and prompts are reused unchanged.

Acceptance criteria:

- Wrapper adds upstream `src` to the Python import path inside the container.
- Wrapper imports the initialized upstream `mcp` object.
- Missing `MEALIE_BASE_URL` or `MEALIE_API_KEY` fails startup clearly, matching upstream behavior.

### Story 02.2: Serve Streamable HTTP

As a remote MCP user, I want to connect to an HTTP endpoint so my MCP client can use the server remotely.

Acceptance criteria:

- Service listens on `MCP_HOST`, default `0.0.0.0`.
- Service listens on `MCP_PORT`, default `8000`.
- MCP endpoint path is `MCP_PATH`, default `/mcp`.
- Default external-facing route after proxying is expected to be `https://<host>/mcp`.
- No TLS is configured inside the container.

### Story 02.3: Avoid Forking Upstream Runtime Logic

As the maintainer, I want wrapper code to stay thin so upstream updates remain easy to consume.

Acceptance criteria:

- Wrapper does not duplicate upstream tool registration code.
- Wrapper does not modify files in `../../3rdParty/mealie-mcp-server`.
- Wrapper-specific behavior lives in this repository.

## Implementation Notes

- Use `uvicorn` to serve the Starlette app returned by FastMCP.
- Prefer `streamable-http` only for the first implementation.
- Do not add SSE unless a client compatibility requirement appears.

## Test Strategy

- Build image using the wrapper Dockerfile.
- Run service against a mock Mealie endpoint that responds to `GET /api/app/about`.
- Use an MCP client to initialize against `http://localhost:8000/mcp` and list tools.
