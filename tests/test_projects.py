from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest

from tedo import PermissionError, Tedo


class Recorder:
    def __init__(self, responses: list[dict[str, Any]] | dict[str, Any], status_code: int = 200) -> None:
        self.requests: list[httpx.Request] = []
        if isinstance(responses, list):
            self._responses = responses
        else:
            self._responses = [responses]
        self._status_code = status_code

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        body = self._responses[min(len(self.requests) - 1, len(self._responses) - 1)]
        return httpx.Response(self._status_code, json=body, request=request)


def test_client_initializes_projects_service() -> None:
    client = Tedo("tedo_live_test", http_client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json={}, request=req))))
    assert client.projects is not None


def test_create_project_sends_idempotency_key_header() -> None:
    recorder = Recorder({"id": "proj-1", "name": "Launch", "description": "Q2", "archived": False})
    client = Tedo("tedo_live_test", base_url="https://api.test", http_client=httpx.Client(transport=httpx.MockTransport(recorder)))

    project = client.projects.create_project({"name": "Launch", "description": "Q2"})

    request = recorder.requests[0]
    assert project["id"] == "proj-1"
    assert request.method == "POST"
    assert request.url.path == "/projects/v1/projects"
    assert request.headers["Authorization"] == "Bearer tedo_live_test"
    assert request.headers["Idempotency-Key"].startswith("tedo_py_")
    assert json.loads(request.content) == {"name": "Launch", "description": "Q2"}
    assert "idempotency_key" not in json.loads(request.content)


def test_request_options_override_idempotency_key_and_request_id() -> None:
    recorder = Recorder({"deleted": True, "id": "proj-1"})
    client = Tedo("tedo_live_test", base_url="https://api.test", http_client=httpx.Client(transport=httpx.MockTransport(recorder)))

    result = client.projects.delete_project("proj-1", idempotency_key="idem_123", request_id="req_123")

    request = recorder.requests[0]
    assert result == {"deleted": True, "id": "proj-1"}
    assert request.headers["Idempotency-Key"] == "idem_123"
    assert request.headers["X-Request-ID"] == "req_123"


def test_list_work_items_encodes_cursor_filters() -> None:
    recorder = Recorder({"items": [], "next_cursor": None, "has_more": False})
    client = Tedo("tedo_live_test", base_url="https://api.test", http_client=httpx.Client(transport=httpx.MockTransport(recorder)))

    page = client.projects.list_work_items_page(
        {
            "project_id": "proj-1",
            "status_id": "status-1",
            "priority": 2,
            "include_completed": True,
            "include_archived": True,
            "limit": 50,
            "cursor": "eyJvZmZzZXQiOjUwfQ",
        }
    )

    request = recorder.requests[0]
    query = parse_qs(request.url.query.decode())
    assert page.has_more is False
    assert request.url.path == "/projects/v1/work-items"
    assert query == {
        "cursor": ["eyJvZmZzZXQiOjUwfQ"],
        "include_archived": ["true"],
        "include_completed": ["true"],
        "limit": ["50"],
        "priority": ["2"],
        "project_id": ["proj-1"],
        "status_id": ["status-1"],
    }


def test_list_projects_generator_fetches_cursor_pages() -> None:
    recorder = Recorder(
        [
            {"items": [{"id": "proj-1"}], "next_cursor": "next", "has_more": True},
            {"items": [{"id": "proj-2"}], "next_cursor": None, "has_more": False},
        ]
    )
    client = Tedo("tedo_live_test", base_url="https://api.test", http_client=httpx.Client(transport=httpx.MockTransport(recorder)))

    ids = [project["id"] for project in client.projects.list_projects({"limit": 1})]

    assert ids == ["proj-1", "proj-2"]
    assert len(recorder.requests) == 2
    assert parse_qs(recorder.requests[1].url.query.decode()) == {"cursor": ["next"], "limit": ["1"]}


def test_list_comments_uses_read_only_endpoint_and_opaque_actor_ref() -> None:
    recorder = Recorder(
        {
            "items": [
                {
                    "id": "comment-1",
                    "work_item_id": "work-1",
                    "actor_type": "api_key",
                    "actor_ref": "api_key:key-1",
                    "content": "ready",
                    "created_at": "2026-05-08T00:00:00Z",
                    "updated_at": "2026-05-08T00:00:00Z",
                }
            ],
            "has_more": False,
        }
    )
    client = Tedo("tedo_live_test", base_url="https://api.test", http_client=httpx.Client(transport=httpx.MockTransport(recorder)))

    comments = client.projects.list_comments_page("work-1").items

    request = recorder.requests[0]
    assert request.method == "GET"
    assert request.url.path == "/projects/v1/work-items/work-1/comments"
    assert comments[0]["actor_ref"] == "api_key:key-1"
    assert "author_id" not in comments[0]
    assert "author_name" not in comments[0]


def test_parse_error_captures_canonical_projects_envelope() -> None:
    recorder = Recorder(
        {
            "code": "permission_denied",
            "message": "API key lacks projects.projects.write",
            "details": {"permission": "projects.projects.write"},
            "request_id": "req_123",
        },
        status_code=403,
    )
    client = Tedo("tedo_live_test", base_url="https://api.test", http_client=httpx.Client(transport=httpx.MockTransport(recorder)))

    with pytest.raises(PermissionError) as excinfo:
        client.projects.create_project({"name": "Denied"})

    err = excinfo.value
    assert err.code == "permission_denied"
    assert err.request_id == "req_123"
    assert err.details == {"permission": "projects.projects.write"}
