# Feature 08: Deployment Examples

## Goal

Provide practical deployment examples for running the container beside Mealie and an HTTPS reverse proxy.

## Status

State: Complete

Stories:

- [x] Story 08.1: Docker Run Example
- [x] Story 08.2: Compose Example For Existing Docker Network
- [x] Story 08.3: Reverse Proxy Notes

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Podman image build succeeded.
- Podman no-compose mock Mealie MCP smoke test succeeded and listed expected tools.
- Docker is unavailable in this environment; Docker-specific commands were not validated separately from Podman.
- Podman Compose provider is unavailable; compose syntax/runtime remains environment-specific/manual.
- Reverse proxy route validation remains deployment-environment-specific/manual.

## Context

The intended production deployment is a Docker host where Mealie already runs. This wrapper should communicate with Mealie over internal Docker networking and be exposed externally only through an HTTPS proxy.

## Stories

### Story 08.1: Docker Run Example

As the operator, I want a minimal `docker run` example for quick manual testing.

Acceptance criteria:

- Example passes env vars from a local `.env` file.
- Example publishes container port `8000` for local testing.
- Example warns not to expose the port publicly without network controls.

### Story 08.2: Compose Example For Existing Docker Network

As the operator, I want a compose example that attaches to an existing Mealie/proxy network.

Acceptance criteria:

- Compose example references the built image or local build context.
- Compose example uses env file configuration.
- Compose example attaches to an external Docker network placeholder.
- Compose example does not include real credentials.

### Story 08.3: Reverse Proxy Notes

As the operator, I want enough proxy guidance to route HTTPS traffic to the internal HTTP service.

Acceptance criteria:

- Documentation identifies upstream target as `http://<container-name>:8000/mcp`.
- Documentation states websocket support is not the core requirement for streamable HTTP, but standard HTTP streaming/proxy buffering behavior should be considered.
- Documentation recommends disabling proxy buffering if streaming behavior is problematic.

## Implementation Notes

- Keep reverse proxy examples generic unless a specific proxy is chosen later.
- If a specific proxy is later requested, add a focused example for it rather than overloading the initial README.

## Test Strategy

- Validate compose file syntax if added.
- Manually confirm proxy route can reach `/mcp` in deployment environment.
