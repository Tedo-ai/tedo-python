# Tedo Python SDK

Official Python SDK for the [Tedo API](https://api.tedo.ai).

## Installation

```bash
pip install tedo
```

## Quick Start

```python
import tedo

client = tedo.Tedo(api_key="tedo_live_xxx")

project = client.projects.create_project(
    {"name": "Public API rollout", "description": "SDK propagation"}
)

work_item = client.projects.create_project_work_item(
    project["id"],
    {"title": "Ship Python bindings", "description": "Typed Projects V1 surface"},
)
```

## Projects

The Projects service covers project CRUD/archive/restore, work item CRUD/complete/archive/restore, subtasks, activity feeds, workflow statuses/types, priority levels, read-only comments, and file-reference attachments.

List helpers are cursor-aware generators:

```python
for item in client.projects.list_work_items({"project_id": project["id"], "limit": 50}):
    print(item["display_id"], item["title"])
```

Manual page access is available via `*_page` methods:

```python
page = client.projects.list_projects_page({"limit": 20})
print(page.items, page.next_cursor, page.has_more)
```

Creates, deletes, and attachment attach/detach calls auto-generate an `Idempotency-Key` when you do not provide one:

```python
project = client.projects.create_project(
    {"name": "Launch"},
    idempotency_key="idem_123",
    request_id="req_123",
)
```

Projects V1 intentionally excludes comment writes, raw multipart upload, live collaborative description editing, bulk operations, and task-named aliases. Attach files by uploading through Files/Storage first, then call `attach_file()` with the `file_id`. Actor fields use opaque references such as `actor_ref` and `created_by_ref`; raw user IDs are not part of the V1 DTOs.

## Error Handling

```python
import tedo

try:
    client.projects.get_project("missing")
except tedo.NotFoundError as err:
    print(err.code, err.request_id)
except tedo.TedoError as err:
    print(err.status_code, err.code, err.details)
```

The SDK parses the canonical `{code, message, details, request_id}` error envelope and raises subclasses for validation, authentication, permission, not-found, and rate-limit failures.

## Typing

The package ships `py.typed`. Projects request and response shapes are exposed as `TypedDict` types, and cents are represented as `int` to match the wire contract.
