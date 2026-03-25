"""Tedo Billing service."""

from .models import Plan, Price, Entitlement


class BillingService:
    """Client for the Tedo Billing API."""

    def __init__(self, client):
        self._client = client

    # ── Plans ──────────────────────────────────────────────

    def list_plans(self):
        """List all plans. Returns a list of Plan objects."""
        data = self._client._request("GET", "/billing/v1/plans")
        return [Plan(p) for p in data.get("plans", [])]

    def get_plan(self, plan_id: str) -> Plan:
        return Plan(self._client._request("GET", f"/billing/v1/plans/{plan_id}"))

    def create_plan(self, *, key: str, name: str, description: str = "") -> Plan:
        return Plan(self._client._request("POST", "/billing/v1/plans", {
            "key": key,
            "name": name,
            "description": description,
        }))

    def update_plan(self, plan_id: str, **kwargs) -> Plan:
        return Plan(self._client._request("PATCH", f"/billing/v1/plans/{plan_id}", kwargs))

    def delete_plan(self, plan_id: str):
        self._client._request_void("DELETE", f"/billing/v1/plans/{plan_id}")

    # ── Prices ─────────────────────────────────────────────

    def create_price(self, *, plan_id: str, key: str, amount_cents: int,
                     currency: str, interval: str) -> Price:
        return Price(self._client._request("POST", f"/billing/v1/plans/{plan_id}/prices", {
            "key": key,
            "amount_cents": amount_cents,
            "currency": currency,
            "interval": interval,
        }))

    def list_prices(self, plan_id: str):
        data = self._client._request("GET", f"/billing/v1/plans/{plan_id}/prices")
        return [Price(p) for p in data.get("prices", [])]

    def archive_price(self, plan_id: str, price_id: str):
        self._client._request_void("DELETE", f"/billing/v1/plans/{plan_id}/prices/{price_id}")

    # ── Entitlements ───────────────────────────────────────

    def create_entitlement(self, *, plan_id: str, key: str,
                           value_bool=None, value_int=None) -> Entitlement:
        body = {"key": key}
        if value_bool is not None:
            body["value_bool"] = value_bool
        if value_int is not None:
            body["value_int"] = value_int
        return Entitlement(self._client._request(
            "POST", f"/billing/v1/plans/{plan_id}/entitlements", body))

    def list_entitlements(self, plan_id: str):
        data = self._client._request("GET", f"/billing/v1/plans/{plan_id}/entitlements")
        return [Entitlement(e) for e in data.get("entitlements", [])]

    def archive_entitlement(self, plan_id: str, entitlement_id: str):
        self._client._request_void(
            "DELETE", f"/billing/v1/plans/{plan_id}/entitlements/{entitlement_id}")
