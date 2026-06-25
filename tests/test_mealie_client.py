from __future__ import annotations

import httpx
import pytest

from mealie.client import MealieApiError, MealieClient


class FakeHTTPClient:
    def __init__(self, response: httpx.Response | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.calls = []

    def request(self, method: str, url: str, **kwargs):
        self.calls.append((method, url, kwargs))
        if self.error:
            raise self.error
        return self.response


def client_with(fake_http_client: FakeHTTPClient) -> MealieClient:
    client = MealieClient.__new__(MealieClient)
    client._client = fake_http_client
    return client


def response(status_code: int, *, json_body=None, text: str | None = None) -> httpx.Response:
    request = httpx.Request("GET", "https://mealie.test/api")
    if json_body is not None:
        return httpx.Response(status_code, json=json_body, request=request)
    return httpx.Response(status_code, text=text or "", request=request)


def test_handle_request_sets_json_content_type_and_returns_json() -> None:
    fake = FakeHTTPClient(response(200, json_body={"ok": True}))
    client = client_with(fake)

    result = client._handle_request("PUT", "/api/recipes/stifado", json={"name": "Stifado"})

    assert result == {"ok": True}
    assert fake.calls == [
        (
            "PUT",
            "/api/recipes/stifado",
            {"json": {"name": "Stifado"}, "headers": {"Content-Type": "application/json"}},
        )
    ]


def test_handle_request_treats_empty_success_as_success_dict() -> None:
    fake = FakeHTTPClient(response(204))
    client = client_with(fake)

    assert client._handle_request("DELETE", "/api/recipes/stifado") == {
        "success": True,
        "message": "Operation completed successfully",
    }


def test_handle_request_raises_mealie_api_error_with_response_details() -> None:
    fake = FakeHTTPClient(response(422, json_body={"detail": "invalid recipe"}))
    client = client_with(fake)

    with pytest.raises(MealieApiError) as exc_info:
        client._handle_request("PUT", "/api/recipes/stifado", json={"bad": True})

    assert exc_info.value.status_code == 422
    assert "invalid recipe" in exc_info.value.message
    assert "invalid recipe" in exc_info.value.response_text


def test_handle_request_maps_timeout_to_timeout_error() -> None:
    fake = FakeHTTPClient(error=httpx.ReadTimeout("slow"))
    client = client_with(fake)

    with pytest.raises(TimeoutError, match="Request timeout"):
        client._handle_request("GET", "/api/recipes")
