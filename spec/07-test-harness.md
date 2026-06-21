# Feature 07: Test Harness

## Goal

Add focused tests for wrapper-owned behavior and documented integration checks for upstream behavior.

## Status

State: Complete

Stories:

- [x] Story 07.1: Unit Tests For Access Control
- [x] Story 07.2: Startup Smoke Test With Mock Mealie
- [x] Story 07.3: MCP Protocol Integration Test
- [x] Story 07.4: Real Mealie Manual Validation

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Python syntax checks passed for wrapper, test, and smoke files.
- Unit tests ran inside the built Podman image and all 8 passed.
- Podman no-compose mock Mealie MCP smoke test succeeded and listed expected tools.
- Docker is unavailable in this environment; Docker-specific commands were not validated separately from Podman.
- Residual risk: mock smoke startup can be readiness-order sensitive; validation passed with the current commands.

## Context

The core Mealie MCP functionality belongs to upstream. This project should test what it owns: packaging, remote transport startup, configuration, and optional subnet filtering. Full Mealie API behavior should be covered only by integration or smoke tests.

## Stories

### Story 07.1: Unit Tests For Access Control

As the maintainer, I want tests for subnet allowlisting because that is security-sensitive wrapper code.

Acceptance criteria:

- Tests cover empty allowlist allows all.
- Tests cover single and multiple CIDRs.
- Tests cover denied client IP.
- Tests cover invalid CIDR failure.

### Story 07.2: Startup Smoke Test With Mock Mealie

As the maintainer, I want to validate startup without depending on a real Mealie instance.

Acceptance criteria:

- Mock service responds successfully to `GET /api/app/about`.
- Container starts with `MEALIE_BASE_URL` pointing at mock service.
- MCP endpoint is reachable over HTTP.

### Story 07.3: MCP Protocol Integration Test

As the maintainer, I want to verify the remote MCP protocol path actually exposes upstream tools.

Acceptance criteria:

- Test client can initialize against `/mcp`.
- Test client can list tools.
- Expected upstream tools are present, such as `get_recipes`, `get_shopping_lists`, and `get_categories`.

### Story 07.4: Real Mealie Manual Validation

As the operator, I want a safe manual validation path against a real Mealie instance.

Acceptance criteria:

- README explains read-only validation first.
- README warns write tests should use disposable data or a test Mealie instance.
- README avoids requiring production credentials in committed files.

## Implementation Notes

- Start with lightweight tests before adding complex compose-based CI.
- Prefer ASGI-level tests for access-control behavior because Docker-level source IP spoofing is awkward.
- Integration tests can be documented/manual initially if automation would add too much scaffolding.

## Test Strategy

- Run Python unit tests locally or inside container.
- Run Docker build test.
- Run mock Mealie smoke test.
- Run optional real Mealie test only when credentials are intentionally supplied.
