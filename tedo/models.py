"""Lightweight attribute-access wrappers over API JSON."""

from __future__ import annotations

from typing import Any


class Model:
    """Base model that allows attribute access on API response dicts."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __getattr__(self, name: str) -> Any:
        return self._data.get(name)

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        id_ = self._data.get("id", "?")
        return f"<{cls} id={id_}>"

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


class Price(Model):
    pass


class Entitlement(Model):
    def get_value(self) -> Any:
        """Return the entitlement value, checking value_int then value_bool then value."""
        if self._data.get("value_int") is not None:
            return self._data["value_int"]
        if self._data.get("value_bool") is not None:
            return self._data["value_bool"]
        return self._data.get("value")


class Plan(Model):
    @property
    def prices(self) -> list[Price] | None:
        raw = self._data.get("prices")
        if not isinstance(raw, list):
            return None
        return [Price(p) for p in raw if isinstance(p, dict)]

    @property
    def entitlements(self) -> list[Entitlement] | None:
        raw = self._data.get("entitlements")
        if not isinstance(raw, list):
            return None
        return [Entitlement(e) for e in raw if isinstance(e, dict)]
