from __future__ import annotations

import ipaddress
import os
import sys
from pathlib import Path
from typing import Iterable

from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_PATH = "/mcp"


def upstream_src_path() -> Path:
    return Path(os.environ.get("MEALIE_MCP_SRC", "/app/mealie-mcp-server/src"))


def normalize_path(path: str | None) -> str:
    if not path:
        return DEFAULT_PATH
    return path if path.startswith("/") else f"/{path}"


def parse_allowed_subnets(raw: str | None) -> list[ipaddress._BaseNetwork]:
    if not raw or not raw.strip():
        return []

    networks: list[ipaddress._BaseNetwork] = []
    for item in raw.split(","):
        value = item.strip()
        if not value:
            continue
        networks.append(ipaddress.ip_network(value, strict=False))
    return networks


def client_is_allowed(client_host: str | None, allowed_subnets: Iterable[ipaddress._BaseNetwork]) -> bool:
    subnets = list(allowed_subnets)
    if not subnets:
        return True
    if not client_host:
        return False

    try:
        client_ip = ipaddress.ip_address(client_host)
    except ValueError:
        return False

    return any(client_ip in subnet for subnet in subnets)


class SubnetAllowlistMiddleware:
    def __init__(self, app: ASGIApp, allowed_subnets: list[ipaddress._BaseNetwork]):
        self.app = app
        self.allowed_subnets = allowed_subnets

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_host = client[0] if client else None
        if not client_is_allowed(client_host, self.allowed_subnets):
            response = PlainTextResponse("Forbidden", status_code=403)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


class LazyApp:
    def __init__(self) -> None:
        self._app: ASGIApp | None = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self._app is None:
            self._app = create_app()
        await self._app(scope, receive, send)


def create_app() -> ASGIApp:
    allowed_subnets = parse_allowed_subnets(os.environ.get("MCP_ALLOWED_SUBNETS"))

    src_path = upstream_src_path()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from server import mcp  # type: ignore[import-not-found]

    mcp.settings.streamable_http_path = normalize_path(os.environ.get("MCP_PATH"))
    app = mcp.streamable_http_app()

    return SubnetAllowlistMiddleware(app, allowed_subnets)


app = LazyApp()


def main() -> None:
    import uvicorn

    host = os.environ.get("MCP_HOST", DEFAULT_HOST)
    port = int(os.environ.get("MCP_PORT", str(DEFAULT_PORT)))
    uvicorn.run(create_app(), host=host, port=port, log_level=os.environ.get("LOG_LEVEL", "INFO").lower())


if __name__ == "__main__":
    main()
