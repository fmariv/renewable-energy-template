"""Pipeline status registry written to storage for API / UI consumption."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

STATUS_PATH = "pipeline_status.json"

IDLE = "Idle"
BUILDING = "Building"
WARNING = "Warning"
ERROR = "Error"
READY = "Ready"

_IDLE = {
    "status": IDLE,
    "message": "No pipeline run yet",
    "updated_at": None,
}


def _row_to_status(df: pd.DataFrame) -> dict:
    """Convert the first DataFrame row to a JSON-serializable status dict."""
    row = df.iloc[0].to_dict()
    out = {}
    for key, value in row.items():
        if pd.isna(value):
            out[key] = None
        elif hasattr(value, "isoformat"):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out


def set_status(storage: Any, status: str, message: str) -> None:
    """Overwrite pipeline status as a records JSON list (readable by storage.read)."""
    payload = {
        "status": status,
        "message": message,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps([payload], ensure_ascii=False)
    try:
        if storage.exists(STATUS_PATH):
            storage.delete(STATUS_PATH)
        storage.create(body, STATUS_PATH)
        logger.info("Pipeline status: %s — %s", status, message)
    except Exception as exc:
        logger.warning("Failed to write pipeline status: %s", exc)


def get_status(storage: Any) -> dict:
    """Read the current pipeline status from storage (pandas → dict)."""
    if not storage.exists(STATUS_PATH):
        return dict(_IDLE)
    try:
        df = storage.read(STATUS_PATH)
        if df is None or (hasattr(df, "empty") and df.empty):
            return dict(_IDLE)
        return _row_to_status(df)
    except Exception as exc:
        logger.warning("Failed to read pipeline status: %s", exc)
        return dict(_IDLE)
