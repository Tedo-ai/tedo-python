"""Projects API bindings."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
import secrets
from typing import Any, Literal, Protocol, TypedDict, TypeVar, cast
from urllib.parse import quote

from .pagination import CursorPage, iter_pages, page_from_response

ProjectStatusCategory = Literal["start", "in_progress", "completed", "canceled"]

PROJECT_STATUS_CATEGORY_START: ProjectStatusCategory = "start"
PROJECT_STATUS_CATEGORY_IN_PROGRESS: ProjectStatusCategory = "in_progress"
PROJECT_STATUS_CATEGORY_COMPLETED: ProjectStatusCategory = "completed"
PROJECT_STATUS_CATEGORY_CANCELED: ProjectStatusCategory = "canceled"

PROJECT_PRIORITY_NONE = 0
PROJECT_PRIORITY_LOW = 1
PROJECT_PRIORITY_MEDIUM = 2
PROJECT_PRIORITY_HIGH = 3
PROJECT_PRIORITY_URGENT = 4

T = TypeVar("T")


class Project(TypedDict, total=False):
    id: str
    team_id: str | None
    name: str
    description: str
    archived: bool
    created_at: str
    updated_at: str


class WorkItem(TypedDict, total=False):
    id: str
    display_id: str
    sequence_number: int
    project_id: str | None
    team_id: str | None
    parent_id: str | None
    work_item_type_id: str | None
    status_id: str | None
    title: str
    description: str
    completed_at: str | None
    archived_at: str | None
    assignee_id: str | None
    priority: int | None
    due_date: str | None
    position: float | None
    child_count: int
    created_at: str
    updated_at: str


class WorkflowStatus(TypedDict, total=False):
    id: str
    work_item_type_id: str | None
    name: str
    category: ProjectStatusCategory | str
    position: int
    is_default: bool
    created_at: str
    updated_at: str


class WorkItemType(TypedDict, total=False):
    id: str
    name: str
    singular_name: str | None
    plural_name: str | None
    parent_type_id: str | None
    prefix: str | None
    color: str | None
    position: int
    show_in_sidebar: bool
    created_at: str
    updated_at: str


class PriorityLevel(TypedDict, total=False):
    id: str
    level: int
    name: str
    icon: str
    created_at: str
    updated_at: str


class ProjectComment(TypedDict, total=False):
    id: str
    work_item_id: str
    actor_type: str
    actor_ref: str
    content: str
    created_at: str
    updated_at: str


class WorkItemActivity(TypedDict, total=False):
    id: str
    actor_type: str
    actor_ref: str
    action: str
    data: dict[str, Any]
    created_at: str


class ProjectAttachment(TypedDict, total=False):
    id: str
    work_item_id: str
    file_id: str
    position: int
    filename: str
    mime_type: str
    size: int
    title: str
    alt_text: str
    created_at: str
    actor_type: str | None
    created_by_ref: str | None


class DeleteResult(TypedDict, total=False):
    deleted: bool
    id: str


class NextDisplayID(TypedDict, total=False):
    display_id: str


class ListProjectsParams(TypedDict, total=False):
    include_archived: bool
    limit: int
    cursor: str


class CreateProjectParams(TypedDict, total=False):
    name: str
    description: str
    team_id: str | None


class UpdateProjectParams(TypedDict, total=False):
    name: str
    description: str | None
    team_id: str | None


class ListWorkItemsParams(TypedDict, total=False):
    project_id: str
    work_item_type_id: str
    status_id: str
    parent_id: str
    assignee_id: str
    priority: int
    include_completed: bool
    include_archived: bool
    limit: int
    cursor: str


class ListPageParams(TypedDict, total=False):
    limit: int
    cursor: str


class ListActivityParams(ListPageParams, total=False):
    include_subtasks: bool
    include_comments: bool


class CreateWorkItemParams(TypedDict, total=False):
    project_id: str | None
    team_id: str | None
    parent_id: str | None
    work_item_type_id: str | None
    status_id: str | None
    title: str
    description: str
    assignee_id: str | None
    priority: int | None
    due_date: str | None
    position: float | None


class UpdateWorkItemParams(TypedDict, total=False):
    project_id: str | None
    team_id: str | None
    parent_id: str | None
    work_item_type_id: str | None
    status_id: str | None
    title: str
    description: str | None
    assignee_id: str | None
    priority: int | None
    due_date: str | None
    position: float | None


class PeekNextDisplayIDParams(TypedDict, total=False):
    work_item_type_id: str


class ListStatusesParams(TypedDict, total=False):
    work_item_type_id: str


class CreateStatusParams(TypedDict, total=False):
    work_item_type_id: str | None
    name: str
    category: ProjectStatusCategory | str
    position: int
    is_default: bool


class UpdateStatusParams(TypedDict, total=False):
    work_item_type_id: str | None
    name: str
    category: ProjectStatusCategory | str
    position: int
    is_default: bool


class CreateWorkItemTypeParams(TypedDict, total=False):
    name: str
    singular_name: str
    plural_name: str
    parent_type_id: str | None
    prefix: str
    color: str
    position: int
    show_in_sidebar: bool


class UpdateWorkItemTypeParams(TypedDict, total=False):
    name: str
    singular_name: str | None
    plural_name: str | None
    parent_type_id: str | None
    prefix: str | None
    color: str | None
    position: int
    show_in_sidebar: bool


class UpdatePriorityLevelParams(TypedDict, total=False):
    name: str
    icon: str


class AttachFileParams(TypedDict, total=False):
    file_id: str
    display_name: str


class RequestOptions(TypedDict, total=False):
    idempotency_key: str
    request_id: str
    headers: Mapping[str, str]


class _Client(Protocol):
    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        query: Mapping[str, str] | None = None,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]: ...


class ProjectsService:
    """Projects service: projects, work items, workflow config, comments, activity, attachments."""

    def __init__(self, client: _Client) -> None:
        self._client = client

    def list_projects_page(self, params: ListProjectsParams | None = None) -> CursorPage[Project]:
        page = self._page("GET", "/projects/v1/projects", query=_list_projects_query(params))
        return _typed_page(page)

    def list_projects(self, params: ListProjectsParams | None = None) -> Iterator[Project]:
        first = self.list_projects_page(params)
        return iter_pages(first, lambda cursor: self.list_projects_page(cast(ListProjectsParams, _with_cursor(params, cursor))))

    def create_project(
        self,
        params: CreateProjectParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Project:
        return cast(Project, self._command("POST", "/projects/v1/projects", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers, idempotency_required=True))

    def get_project(self, project_id: str) -> Project:
        return cast(Project, self._client._request("GET", f"/projects/v1/projects/{_path(project_id)}"))

    def update_project(
        self,
        project_id: str,
        params: UpdateProjectParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Project:
        return cast(Project, self._command("PATCH", f"/projects/v1/projects/{_path(project_id)}", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def archive_project(
        self,
        project_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Project:
        return self._project_action(project_id, "archive", idempotency_key=idempotency_key, request_id=request_id, headers=headers)

    def restore_project(
        self,
        project_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Project:
        return self._project_action(project_id, "restore", idempotency_key=idempotency_key, request_id=request_id, headers=headers)

    def delete_project(
        self,
        project_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> DeleteResult:
        return cast(DeleteResult, self._command("DELETE", f"/projects/v1/projects/{_path(project_id)}", None, idempotency_key=idempotency_key, request_id=request_id, headers=headers, idempotency_required=True))

    def list_project_work_items_page(
        self,
        project_id: str,
        params: ListWorkItemsParams | None = None,
    ) -> CursorPage[WorkItem]:
        page = self._page("GET", f"/projects/v1/projects/{_path(project_id)}/work-items", query=_work_item_query(params, include_project_id=False))
        return _typed_page(page)

    def list_project_work_items(
        self,
        project_id: str,
        params: ListWorkItemsParams | None = None,
    ) -> Iterator[WorkItem]:
        first = self.list_project_work_items_page(project_id, params)
        return iter_pages(first, lambda cursor: self.list_project_work_items_page(project_id, cast(ListWorkItemsParams, _with_cursor(params, cursor))))

    def create_project_work_item(
        self,
        project_id: str,
        params: CreateWorkItemParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItem:
        body = dict(params)
        body["project_id"] = project_id
        return cast(WorkItem, self._command("POST", f"/projects/v1/projects/{_path(project_id)}/work-items", body, idempotency_key=idempotency_key, request_id=request_id, headers=headers, idempotency_required=True))

    def list_work_items_page(self, params: ListWorkItemsParams | None = None) -> CursorPage[WorkItem]:
        page = self._page("GET", "/projects/v1/work-items", query=_work_item_query(params, include_project_id=True))
        return _typed_page(page)

    def list_work_items(self, params: ListWorkItemsParams | None = None) -> Iterator[WorkItem]:
        first = self.list_work_items_page(params)
        return iter_pages(first, lambda cursor: self.list_work_items_page(cast(ListWorkItemsParams, _with_cursor(params, cursor))))

    def create_work_item(
        self,
        params: CreateWorkItemParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItem:
        return cast(WorkItem, self._command("POST", "/projects/v1/work-items", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers, idempotency_required=True))

    def peek_next_display_id(self, params: PeekNextDisplayIDParams | None = None) -> NextDisplayID:
        return cast(NextDisplayID, self._client._request("GET", "/projects/v1/work-items/next-display-id", query=_compact_query(params or {})))

    def get_work_item(self, work_item_id: str) -> WorkItem:
        return cast(WorkItem, self._client._request("GET", f"/projects/v1/work-items/{_path(work_item_id)}"))

    def update_work_item(
        self,
        work_item_id: str,
        params: UpdateWorkItemParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItem:
        return cast(WorkItem, self._command("PATCH", f"/projects/v1/work-items/{_path(work_item_id)}", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def complete_work_item(
        self,
        work_item_id: str,
        completed: bool = True,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItem:
        return cast(WorkItem, self._command("POST", f"/projects/v1/work-items/{_path(work_item_id)}/complete", {"completed": completed}, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def archive_work_item(
        self,
        work_item_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItem:
        return self._work_item_action(work_item_id, "archive", idempotency_key=idempotency_key, request_id=request_id, headers=headers)

    def restore_work_item(
        self,
        work_item_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItem:
        return self._work_item_action(work_item_id, "restore", idempotency_key=idempotency_key, request_id=request_id, headers=headers)

    def delete_work_item(
        self,
        work_item_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> DeleteResult:
        return cast(DeleteResult, self._command("DELETE", f"/projects/v1/work-items/{_path(work_item_id)}", None, idempotency_key=idempotency_key, request_id=request_id, headers=headers, idempotency_required=True))

    def list_subtasks_page(self, work_item_id: str, params: ListPageParams | None = None) -> CursorPage[WorkItem]:
        page = self._page("GET", f"/projects/v1/work-items/{_path(work_item_id)}/subtasks", query=_compact_query(params or {}))
        return _typed_page(page)

    def list_subtasks(self, work_item_id: str, params: ListPageParams | None = None) -> Iterator[WorkItem]:
        first = self.list_subtasks_page(work_item_id, params)
        return iter_pages(first, lambda cursor: self.list_subtasks_page(work_item_id, cast(ListPageParams, _with_cursor(params, cursor))))

    def list_work_item_activity_page(self, work_item_id: str, params: ListActivityParams | None = None) -> CursorPage[WorkItemActivity]:
        page = self._page("GET", f"/projects/v1/work-items/{_path(work_item_id)}/activity", query=_compact_query(params or {}))
        return _typed_page(page)

    def list_work_item_activity(self, work_item_id: str, params: ListActivityParams | None = None) -> Iterator[WorkItemActivity]:
        first = self.list_work_item_activity_page(work_item_id, params)
        return iter_pages(first, lambda cursor: self.list_work_item_activity_page(work_item_id, cast(ListActivityParams, _with_cursor(params, cursor))))

    def list_statuses_page(self, params: ListStatusesParams | None = None) -> CursorPage[WorkflowStatus]:
        page = self._page("GET", "/projects/v1/statuses", query=_compact_query(params or {}))
        return _typed_page(page)

    def list_statuses(self, params: ListStatusesParams | None = None) -> Iterator[WorkflowStatus]:
        return iter(self.list_statuses_page(params).items)

    def create_status(
        self,
        params: CreateStatusParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkflowStatus:
        return cast(WorkflowStatus, self._command("POST", "/projects/v1/statuses", params, idempotency_required=True, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def update_status(
        self,
        status_id: str,
        params: UpdateStatusParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkflowStatus:
        return cast(WorkflowStatus, self._command("PATCH", f"/projects/v1/statuses/{_path(status_id)}", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def delete_status(
        self,
        status_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> DeleteResult:
        return cast(DeleteResult, self._command("DELETE", f"/projects/v1/statuses/{_path(status_id)}", None, idempotency_required=True, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def list_work_item_types_page(self) -> CursorPage[WorkItemType]:
        page = self._page("GET", "/projects/v1/work-item-types")
        return _typed_page(page)

    def list_work_item_types(self) -> Iterator[WorkItemType]:
        return iter(self.list_work_item_types_page().items)

    def create_work_item_type(
        self,
        params: CreateWorkItemTypeParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItemType:
        return cast(WorkItemType, self._command("POST", "/projects/v1/work-item-types", params, idempotency_required=True, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def update_work_item_type(
        self,
        work_item_type_id: str,
        params: UpdateWorkItemTypeParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItemType:
        return cast(WorkItemType, self._command("PATCH", f"/projects/v1/work-item-types/{_path(work_item_type_id)}", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def delete_work_item_type(
        self,
        work_item_type_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> DeleteResult:
        return cast(DeleteResult, self._command("DELETE", f"/projects/v1/work-item-types/{_path(work_item_type_id)}", None, idempotency_required=True, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def list_priority_levels_page(self) -> CursorPage[PriorityLevel]:
        page = self._page("GET", "/projects/v1/priority-levels")
        return _typed_page(page)

    def list_priority_levels(self) -> Iterator[PriorityLevel]:
        return iter(self.list_priority_levels_page().items)

    def update_priority_level(
        self,
        level: int,
        params: UpdatePriorityLevelParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> PriorityLevel:
        return cast(PriorityLevel, self._command("PATCH", f"/projects/v1/priority-levels/{level}", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def reset_priority_level(
        self,
        level: int,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> PriorityLevel:
        return cast(PriorityLevel, self._command("POST", f"/projects/v1/priority-levels/{level}/reset", None, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def list_comments_page(self, work_item_id: str, params: ListPageParams | None = None) -> CursorPage[ProjectComment]:
        page = self._page("GET", f"/projects/v1/work-items/{_path(work_item_id)}/comments", query=_compact_query(params or {}))
        return _typed_page(page)

    def list_comments(self, work_item_id: str, params: ListPageParams | None = None) -> Iterator[ProjectComment]:
        first = self.list_comments_page(work_item_id, params)
        return iter_pages(first, lambda cursor: self.list_comments_page(work_item_id, cast(ListPageParams, _with_cursor(params, cursor))))

    def list_attachments_page(self, work_item_id: str) -> CursorPage[ProjectAttachment]:
        page = self._page("GET", f"/projects/v1/work-items/{_path(work_item_id)}/attachments")
        return _typed_page(page)

    def list_attachments(self, work_item_id: str) -> Iterator[ProjectAttachment]:
        return iter(self.list_attachments_page(work_item_id).items)

    def attach_file(
        self,
        work_item_id: str,
        params: AttachFileParams,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> ProjectAttachment:
        return cast(ProjectAttachment, self._command("POST", f"/projects/v1/work-items/{_path(work_item_id)}/attachments", params, idempotency_key=idempotency_key, request_id=request_id, headers=headers, idempotency_required=True))

    def detach_attachment(
        self,
        work_item_id: str,
        attachment_id: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> DeleteResult:
        path = f"/projects/v1/work-items/{_path(work_item_id)}/attachments/{_path(attachment_id)}"
        return cast(DeleteResult, self._command("DELETE", path, None, idempotency_key=idempotency_key, request_id=request_id, headers=headers, idempotency_required=True))

    def _project_action(
        self,
        project_id: str,
        action: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Project:
        return cast(Project, self._command("POST", f"/projects/v1/projects/{_path(project_id)}/{action}", None, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def _work_item_action(
        self,
        work_item_id: str,
        action: str,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkItem:
        return cast(WorkItem, self._command("POST", f"/projects/v1/work-items/{_path(work_item_id)}/{action}", None, idempotency_key=idempotency_key, request_id=request_id, headers=headers))

    def _command(
        self,
        method: str,
        path: str,
        body: Mapping[str, Any] | None,
        *,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
        idempotency_required: bool = False,
    ) -> dict[str, Any]:
        key = idempotency_key
        if idempotency_required and not key:
            key = _new_idempotency_key()
        return self._client._request(method, path, body=body, idempotency_key=key, request_id=request_id, headers=headers)

    def _page(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, str] | None = None,
    ) -> CursorPage[dict[str, Any]]:
        return page_from_response(self._client._request(method, path, query=query))


def _typed_page(page: CursorPage[dict[str, Any]]) -> CursorPage[T]:
    return CursorPage(items=[cast(T, item) for item in page.items], next_cursor=page.next_cursor, has_more=page.has_more)


def _list_projects_query(params: ListProjectsParams | None) -> dict[str, str] | None:
    return _compact_query(params or {})


def _work_item_query(params: ListWorkItemsParams | None, *, include_project_id: bool) -> dict[str, str] | None:
    values = dict(params or {})
    if not include_project_id:
        values.pop("project_id", None)
    return _compact_query(values)


def _compact_query(values: Mapping[str, object]) -> dict[str, str] | None:
    query: dict[str, str] = {}
    for key, value in values.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            query[key] = "true" if value else "false"
        else:
            query[key] = str(value)
    return query or None


def _with_cursor(params: Mapping[str, Any] | None, cursor: str) -> dict[str, Any]:
    values = dict(params or {})
    values["cursor"] = cursor
    return values


def _path(value: str) -> str:
    return quote(value, safe="")


def _new_idempotency_key() -> str:
    return "tedo_py_" + secrets.token_hex(16)
