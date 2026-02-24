"""JSON helpers with optional orjson support."""

try:
    import orjson as _json

    def json_loads(b: bytes):
        return _json.loads(b)

    def json_dumps(obj) -> str:
        return _json.dumps(obj).decode("utf-8")
except Exception:
    import json as _json

    def json_loads(b: bytes):
        if isinstance(b, (bytes, bytearray)):
            try:
                return _json.loads(b)
            except Exception:
                return _json.loads(b.decode("utf-8", "ignore"))
        return _json.loads(b)

    def json_dumps(obj) -> str:
        return _json.dumps(obj)
