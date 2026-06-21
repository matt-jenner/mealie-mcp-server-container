# Feature 05: Configuration And Secrets

## Goal

Define runtime configuration and secret handling for the container without committing credentials.

## Status

State: Complete

Stories:

- [x] Story 05.1: Environment Template
- [x] Story 05.2: Required Mealie Configuration
- [x] Story 05.3: Wrapper Runtime Configuration

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Missing required Mealie env vars fail startup with upstream `ValueError`.
- Invalid `MCP_ALLOWED_SUBNETS` fails startup before upstream import.
- Podman image build succeeded; unit tests ran inside the built image and all 8 passed.
- Docker is unavailable in this environment; Docker-specific commands were not validated separately from Podman.
- Repository-root `.dockerignore` excludes `.env` from build context.

## Context

The upstream MCP server requires `MEALIE_BASE_URL` and `MEALIE_API_KEY`. The wrapper adds HTTP server configuration and optional subnet allowlisting. The Mealie API key should be provided only at runtime.

## Stories

### Story 05.1: Environment Template

As the operator, I want a safe example env file so required configuration is discoverable without exposing secrets.

Acceptance criteria:

- `.env.example` documents all supported env vars.
- `.env.example` contains placeholder values only.
- `.env` is ignored by git.

### Story 05.2: Required Mealie Configuration

As the operator, I want startup to fail clearly when Mealie configuration is missing.

Acceptance criteria:

- `MEALIE_BASE_URL` is required.
- `MEALIE_API_KEY` is required.
- Startup validates Mealie connectivity through upstream initialization.

### Story 05.3: Wrapper Runtime Configuration

As the operator, I want predictable defaults for HTTP serving and optional access control.

Acceptance criteria:

- `MCP_HOST` defaults to `0.0.0.0`.
- `MCP_PORT` defaults to `8000`.
- `MCP_PATH` defaults to `/mcp`.
- `MCP_ALLOWED_SUBNETS` defaults to empty allow-all behavior.
- `LOG_LEVEL` defaults to upstream behavior of `INFO`.

## Implementation Notes

- Do not add default API keys or realistic secrets anywhere.
- Document Docker secrets or orchestrator-managed env vars as production-friendly options, but keep the first implementation env-var based.

## Test Strategy

- Confirm `.env` is ignored.
- Confirm missing required env vars fail startup.
- Confirm `.env.example` contains no secrets.
