"""Tedo SDK data models — lightweight attribute-access wrappers over API JSON."""


class _Model:
    """Base model that allows attribute access on API response dicts."""

    def __init__(self, data: dict):
        self._data = data

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            return None

    def __repr__(self):
        cls = self.__class__.__name__
        id_ = self._data.get("id", "?")
        return f"<{cls} id={id_}>"


class Plan(_Model):
    @property
    def prices(self):
        raw = self._data.get("prices")
        if raw is None:
            return None
        return [Price(p) for p in raw]

    @property
    def entitlements(self):
        raw = self._data.get("entitlements")
        if raw is None:
            return None
        return [Entitlement(e) for e in raw]


class Price(_Model):
    pass


class Entitlement(_Model):
    def get_value(self):
        """Return the entitlement value, checking value_int then value_bool then value."""
        if self._data.get("value_int") is not None:
            return self._data["value_int"]
        if self._data.get("value_bool") is not None:
            return self._data["value_bool"]
        return self._data.get("value")
