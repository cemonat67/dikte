from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from agents.intake_core.src.metric_registry import load_registered_metrics
from agents.intake_core.src.preflight_validator import validate_csv_preflight


def run_csv_preflight(file_bytes: bytes, file_name: str, db_url: str | None = None) -> Dict[str, Any]:
    db_url = db_url or os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set")

    suffix = Path(file_name).suffix or ".csv"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        registered = load_registered_metrics(db_url)
        result = validate_csv_preflight(tmp_path, registered_metrics=registered)
        data = result.to_dict()
        data["original_file_name"] = file_name
        return data
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
