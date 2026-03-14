import hashlib
import json
from typing import Any


def stable_json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_source_hash(payload: Any) -> str:
    raw = stable_json_dumps(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
