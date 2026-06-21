# Feature 03: Container Build

## Goal

Build a reproducible Docker image that packages the upstream MCP server and wrapper runtime with pinned dependencies.

## Status

State: Complete

Stories:

- [x] Story 03.1: Dockerfile Builds From Repository Root
- [x] Story 03.2: Pinned Upstream Source Is Fetched During Build
- [x] Story 03.3: Dependencies Are Locked
- [x] Story 03.4: Runtime Command Starts Remote Wrapper

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Repository-root Podman build succeeded with `podman build -t mealie-mcp-server-container .`.
- Dockerfile fetches pinned upstream ref `f7a2a5e21e68e223629393a5ad16f55dca6ea577` during build.
- Missing required Mealie env vars fail startup with upstream `ValueError`.
- Invalid `MCP_ALLOWED_SUBNETS` fails startup before upstream import.
- Unit tests ran inside the built Podman image and all 8 passed.
- Podman no-compose mock Mealie MCP smoke test succeeded and listed expected tools.
- Docker CLI is unavailable in this environment; Docker-specific command validation remains to be run on a Docker host.

## Context

The host does not currently have `uv` installed, and the upstream repository uses `uv.lock`. The Docker build should therefore provide `uv` inside the image, download a pinned upstream source archive, and install dependencies using the upstream lockfile.

## Stories

### Story 03.1: Dockerfile Builds From Repository Root

As an operator, I want the Dockerfile to build from this repository root so any user can build the image from a normal clone of this wrapper repository.

Acceptance criteria:

- Build command works from this repository root with `docker build -t mealie-mcp-server-container .`.
- Podman equivalent works from this repository root with `podman build -t mealie-mcp-server-container .`.
- Dockerfile path is `Dockerfile` at this repository root.
- Build does not depend on sibling directories such as `../../3rdParty` or `../../personal`.

### Story 03.2: Pinned Upstream Source Is Fetched During Build

As the maintainer, I want the image build to fetch a specific upstream `rldiao/mealie-mcp-server` source ref so the image is reproducible without vendoring upstream source.

Acceptance criteria:

- Dockerfile defines `MEALIE_MCP_REPO` build arg defaulting to `https://github.com/rldiao/mealie-mcp-server`.
- Dockerfile defines `MEALIE_MCP_REF` build arg defaulting to full commit SHA `f7a2a5e21e68e223629393a5ad16f55dca6ea577`.
- Build downloads the upstream archive for `MEALIE_MCP_REF` during image build.
- Build extracts upstream into `/app/mealie-mcp-server`.
- README documents how to override `MEALIE_MCP_REF` if upstream later publishes tags or a newer commit is intentionally selected.

### Story 03.3: Dependencies Are Locked

As the maintainer, I want dependency versions to match upstream lockfile so FastMCP API behavior remains stable.

Acceptance criteria:

- Image uses Python 3.12.
- Image includes `uv`.
- Build runs `uv sync --frozen --no-dev` in the copied upstream project.
- Build fails if `uv.lock` and `pyproject.toml` are inconsistent.

### Story 03.4: Runtime Command Starts Remote Wrapper

As the operator, I want the container default command to start the remote HTTP MCP service.

Acceptance criteria:

- Default command starts the wrapper server.
- Container exits non-zero if required Mealie env vars are missing.
- Container exposes port `8000` for documentation/discovery.

## Implementation Notes

- Recommended base image: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`.
- Keep image minimal, but do not optimize prematurely with complex multi-stage builds unless needed.
- Avoid baking secrets into the image.

## Test Strategy

- Run `docker build -t mealie-mcp-server-container .` from this repository root.
- Run `podman build -t mealie-mcp-server-container .` from this repository root when Docker is unavailable.
- Run container with missing env vars and confirm clear failure.
- Run container with mock Mealie env vars and confirm HTTP server starts.
