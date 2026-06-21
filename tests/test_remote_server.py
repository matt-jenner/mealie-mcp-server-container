from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from remote_server import SubnetAllowlistMiddleware, client_is_allowed, create_app, normalize_path, parse_allowed_subnets


async def ok_app(scope, receive, send):
    from starlette.responses import PlainTextResponse

    response = PlainTextResponse("ok")
    await response(scope, receive, send)


def test_normalize_path_defaults_and_adds_slash() -> None:
    assert normalize_path(None) == "/mcp"
    assert normalize_path("") == "/mcp"
    assert normalize_path("mcp") == "/mcp"
    assert normalize_path("/custom") == "/custom"


def test_empty_allowed_subnets_allows_all() -> None:
    assert parse_allowed_subnets(None) == []
    assert parse_allowed_subnets("") == []
    assert client_is_allowed("203.0.113.10", []) is True


def test_allowed_subnets_match_ipv4_and_ipv6() -> None:
    subnets = parse_allowed_subnets("192.168.1.0/24,2001:db8::/32")
    assert client_is_allowed("192.168.1.42", subnets) is True
    assert client_is_allowed("2001:db8::1", subnets) is True
    assert client_is_allowed("192.168.2.42", subnets) is False


def test_invalid_subnet_fails_fast() -> None:
    with pytest.raises(ValueError):
        parse_allowed_subnets("not-a-cidr")


def test_middleware_allows_matching_client() -> None:
    app = SubnetAllowlistMiddleware(ok_app, parse_allowed_subnets("192.168.1.0/24"))
    client = TestClient(app, client=("192.168.1.42", 50000))
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "ok"


def test_middleware_denies_non_matching_client() -> None:
    app = SubnetAllowlistMiddleware(ok_app, parse_allowed_subnets("192.0.2.0/24"))
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 403
    assert response.text == "Forbidden"


def test_middleware_does_not_trust_x_forwarded_for() -> None:
    app = SubnetAllowlistMiddleware(ok_app, parse_allowed_subnets("192.0.2.0/24"))
    client = TestClient(app, client=("198.51.100.10", 50000))
    response = client.get("/", headers={"X-Forwarded-For": "192.0.2.42"})
    assert response.status_code == 403


def test_create_app_fails_on_invalid_allowed_subnet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_ALLOWED_SUBNETS", "not-a-cidr")
    with pytest.raises(ValueError):
        create_app()
