"""
Portable FastAPI helpers for pipeline status.

Copy the functions into ``apis/<name>/main.py`` (or a local ``src/`` module),
or paste ``read_pipeline_status`` next to your routes.

Never raise HTTP 500 from the status poller — the UI must keep working.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

DEFAULT_STATUS_PATH = "pipeline_status.json"

_IDLE = {
    "status": "Idle",
    "message": "No pipeline run yet",
    "updated_at": None,
}


def read_pipeline_status(
    storage: Any,
    path: str = DEFAULT_STATUS_PATH,
) -> dict:
    """Read ``pipeline_status.json`` from storage as a JSON-serializable dict."""
    if not storage.exists(path):
        return dict(_IDLE)
    try:
        df = storage.read(path)
        if df is None or df.empty:
            return dict(_IDLE)
        row = df.iloc[0]
        out = {}
        for key, value in row.items():
            if pd.isna(value):
                out[key] = None
            elif hasattr(value, "isoformat"):
                out[key] = value.isoformat()
            elif hasattr(value, "item"):
                out[key] = value.item()
            else:
                out[key] = value
        if out.get("status") is not None:
            out["status"] = str(out["status"]).strip()
        if out.get("message") is not None:
            out["message"] = str(out["message"])
        return out
    except Exception:
        return dict(_IDLE)


def data_available_payload(pipeline: Optional[dict] = None) -> dict:
    """Build the standard ``/data_available`` response from a status dict."""
    pipeline = pipeline or dict(_IDLE)
    ready = pipeline.get("status") == "Ready"
    return {
        "status": "healthy",
        "data_available": ready,
        "data_status": "ready" if ready else "no_data",
        "pipeline_status": pipeline.get("status"),
        "message": pipeline.get("message"),
    }
