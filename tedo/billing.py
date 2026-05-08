"""Tedo Billing service."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from .models import Entitlement, Plan, Price


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

    def _request_void(
        self,
        method: str,
        path: str,
        *,
        body: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
        request_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None: ...


class BillingService:
    """Client for the Tedo Billing API."""

    def __init__(self, client: _Client) -> None:
        self._client = client

    def list_plans(self) -> list[Plan]:
        data = self._client._request("GET", "/billing/v1/plans")
        raw_plans = data.get("plans", [])
        if not isinstance(raw_plans, list):
            return []
        return [Plan(p) for p in raw_plans if isinstance(p, dict)]

    def get_plan(self, plan_id: str) -> Plan:
        return Plan(self._client._request("GET", f"/billing/v1/plans/{plan_id}"))

    def create_plan(self, *, key: str, name: str, description: str = "") -> Plan:
        return Plan(
            self._client._request(
                "POST",
                "/billing/v1/plans",
                body={"key": key, "name": name, "description": description},
            )
        )

    def update_plan(self, plan_id: str, **kwargs: Any) -> Plan:
        return Plan(self._client._request("PATCH", f"/billing/v1/plans/{plan_id}", body=kwargs))

    def delete_plan(self, plan_id: str) -> None:
        self._client._request_void("DELETE", f"/billing/v1/plans/{plan_id}")

    def create_price(
        self,
        *,
        plan_id: str,
        key: str,
        amount_cents: int,
        currency: str,
        interval: str,
    ) -> Price:
        return Price(
            self._client._request(
                "POST",
                f"/billing/v1/plans/{plan_id}/prices",
                body={
                    "key": key,
                    "amount_cents": amount_cents,
                    "currency": currency,
                    "interval": interval,
                },
            )
        )

    def list_prices(self, plan_id: str) -> list[Price]:
        data = self._client._request("GET", f"/billing/v1/plans/{plan_id}/prices")
        raw_prices = data.get("prices", [])
        if not isinstance(raw_prices, list):
            return []
        return [Price(p) for p in raw_prices if isinstance(p, dict)]

    def archive_price(self, plan_id: str, price_id: str) -> None:
        self._client._request_void("DELETE", f"/billing/v1/plans/{plan_id}/prices/{price_id}")

    def create_entitlement(
        self,
        *,
        plan_id: str,
        key: str,
        value_bool: bool | None = None,
        value_int: int | None = None,
    ) -> Entitlement:
        body: dict[str, Any] = {"key": key}
        if value_bool is not None:
            body["value_bool"] = value_bool
        if value_int is not None:
            body["value_int"] = value_int
        return Entitlement(
            self._client._request(
                "POST",
                f"/billing/v1/plans/{plan_id}/entitlements",
                body=body,
            )
        )

    def list_entitlements(self, plan_id: str) -> list[Entitlement]:
        data = self._client._request("GET", f"/billing/v1/plans/{plan_id}/entitlements")
        raw_entitlements = data.get("entitlements", [])
        if not isinstance(raw_entitlements, list):
            return []
        return [Entitlement(e) for e in raw_entitlements if isinstance(e, dict)]

    def archive_entitlement(self, plan_id: str, entitlement_id: str) -> None:
        self._client._request_void(
            "DELETE",
            f"/billing/v1/plans/{plan_id}/entitlements/{entitlement_id}",
        )
