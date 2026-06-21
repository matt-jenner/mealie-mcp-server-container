# Feature 04: Network Access Control

## Goal

Provide an optional in-container subnet allowlist as a second-level access check for the unauthenticated remote MCP endpoint.

## Status

State: Complete

Stories:

- [x] Story 04.1: Optional CIDR Allowlist
- [x] Story 04.2: Direct Peer IP Enforcement
- [x] Story 04.3: Reverse Proxy Guidance

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Python syntax checks passed for wrapper, test, and smoke files.
- Invalid `MCP_ALLOWED_SUBNETS` fails startup before upstream import.
- Unit tests ran inside the built Podman image and all 8 passed.
- Reverse proxy route validation remains deployment-environment-specific/manual.

## Context

The container will hold a Mealie API key and remote MCP users will not authenticate to the MCP server. Any caller that reaches the MCP endpoint can indirectly act through that Mealie API key. Network/proxy controls are the primary defense; app-level CIDR filtering is an additional guardrail.

## Stories

### Story 04.1: Optional CIDR Allowlist

As the operator, I want to optionally restrict access by source subnet so only expected internal/proxy networks can call the MCP endpoint.

Acceptance criteria:

- Env var `MCP_ALLOWED_SUBNETS` accepts a comma-separated list of CIDR ranges.
- Empty or unset `MCP_ALLOWED_SUBNETS` allows all clients.
- Invalid CIDR values fail startup with a clear error.
- IPv4 and IPv6 CIDRs are handled by standard library parsing.

### Story 04.2: Direct Peer IP Enforcement

As the operator, I want source checks to avoid trusting spoofable headers by default.

Acceptance criteria:

- Middleware checks the direct ASGI client IP from the request scope.
- Middleware does not trust `X-Forwarded-For` by default.
- Requests from outside allowed CIDRs receive HTTP `403 Forbidden`.

### Story 04.3: Reverse Proxy Guidance

As the operator, I want clear documentation for using the allowlist behind an HTTPS proxy.

Acceptance criteria:

- README explains that the app will usually see the proxy IP, not the original client IP.
- README recommends primary allowlisting at the proxy/firewall/VPN layer.
- README explains that `MCP_ALLOWED_SUBNETS` should include the proxy/container subnet if enabled behind a proxy.

## Implementation Notes

- Implement as Starlette middleware around the FastMCP streamable HTTP app.
- Keep trusted proxy header support out of the first version unless explicitly required.

## Test Strategy

- Unit test CIDR parsing and allow/deny decisions.
- ASGI-level test verifies allowed IP returns non-403 and denied IP returns 403.
- Manual deployment test verifies proxy/network behavior separately.
