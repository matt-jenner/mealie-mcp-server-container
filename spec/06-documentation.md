# Feature 06: Documentation

## Goal

Provide a valid README that explains what this project is, how to build it, how to run it, how to deploy it behind HTTPS, and what the security model is.

## Status

State: Complete

Stories:

- [x] Story 06.1: Project Purpose Is Clear
- [x] Story 06.2: Build And Run Instructions Exist
- [x] Story 06.3: Reverse Proxy Deployment Is Explained
- [x] Story 06.4: Security Model Is Explicit
- [x] Story 06.5: Testing Instructions Exist

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Podman image build succeeded; unit tests ran inside the built image and all 8 passed.
- Podman no-compose mock Mealie MCP smoke test succeeded and listed expected tools.
- Docker is unavailable in this environment; Docker-specific commands were not validated separately from Podman.
- Podman Compose provider is unavailable; compose syntax/runtime remains environment-specific/manual.
- Reverse proxy route validation remains deployment-environment-specific/manual.
- README now documents repository-root build and pinned upstream ref override.

## Context

This project is a Docker remote-HTTP wrapper around an upstream Mealie MCP server. Operators need clear guidance because the MCP endpoint is intentionally unauthenticated and uses a server-side Mealie API key.

## Stories

### Story 06.1: Project Purpose Is Clear

As a reader, I want to understand what this repository contains and what it does not contain.

Acceptance criteria:

- README names upstream project `rldiao/mealie-mcp-server`.
- README states this repository is a wrapper/container project.
- README states upstream MCP logic is reused rather than reimplemented.

### Story 06.2: Build And Run Instructions Exist

As the operator, I want concrete commands for building and running the container.

Acceptance criteria:

- README includes Docker build command from this repository root.
- README includes `docker run` example with `--env-file` and port publishing.
- README includes example internal endpoint `http://localhost:8000/mcp`.

### Story 06.3: Reverse Proxy Deployment Is Explained

As the operator, I want guidance for running internal HTTP behind external HTTPS.

Acceptance criteria:

- README states the container serves HTTP only.
- README states HTTPS should terminate at the reverse proxy.
- README shows external MCP URL shape `https://<domain>/mcp`.
- README includes notes for Docker network placement with Mealie and proxy.

### Story 06.4: Security Model Is Explicit

As the operator, I want the risk model documented so I do not accidentally expose Mealie write access publicly.

Acceptance criteria:

- README states remote MCP users do not authenticate to this container.
- README states anyone who reaches the endpoint can use capabilities granted by the configured Mealie API key.
- README recommends firewall, VPN, proxy allowlist, or private network controls as primary protection.
- README explains `MCP_ALLOWED_SUBNETS` as a second-level check.

### Story 06.5: Testing Instructions Exist

As the maintainer, I want documented validation steps so changes can be checked consistently.

Acceptance criteria:

- README includes build validation.
- README includes startup smoke test guidance.
- README includes MCP initialize/list-tools validation guidance.
- README distinguishes mock Mealie tests from real Mealie tests.

## Implementation Notes

- README should be useful before and after publishing a first image.
- Keep commands copy-pasteable, but avoid embedding real secrets.

## Test Strategy

- Review README for accuracy against actual files and commands.
- Run documented build/run commands where possible.
