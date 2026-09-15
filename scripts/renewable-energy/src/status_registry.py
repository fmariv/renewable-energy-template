"""
Portable pipeline status registry for SPAI templates.

Copy this file into each template as:
  scripts/<script-name>/src/status_registry.py

Contract written to storage (one-row DataFrame JSON):
  { "status": "Idle|Building|Warning|Error|Ready", "message": "...", "updated_at": "..." }

Error messages shown to the UI are always generic — keep technical detail in logs only.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Override per template if you use AOI-scoped paths, e.g. "shared/results/analytics/pipeline_status.json"
STATUS_PATH = "pipeline_status.json"
MAX_MESSAGE_LEN = 240

IDLE = "Idle"
BUILDING = "Building"
WARNING = "Warning"
ERROR = "Error"
READY = "Ready"

# User-facing error copy (UI + registry). Details belong in application logs.
GENERIC_ERROR_MESSAGE = (
    "Error downloading data. Check the logs or contact support."
)
GENERIC_ERROR_TITLE = "Error downloading data"
GENERIC_ERROR_DETAIL = "Check the logs or contact support."

_IDLE = {
    "status": IDLE,
    "message": "No pipeline run yet",
    "updated_at": None,
}


def _clip(message: str) -> str:
    text = " ".join((message or "").split())
    if len(text) > MAX_MESSAGE_LEN:
        return text[: MAX_MESSAGE_LEN - 1].rstrip() + "…"
    return text


def _public_message(status: str, message: str) -> str:
    if status == ERROR:
        return GENERIC_ERROR_MESSAGE
    return _clip(message)


def _row_to_status(df: pd.DataFrame) -> dict:
    row = df.iloc[0].to_dict()
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


def set_status(
    storage: Any,
    status: str,
    message: str = "",
    *,
    path: Optional[str] = None,
) -> None:
    """
    Overwrite current pipeline status in storage.

    Uses a one-row DataFrame so ``storage.read("*.json")`` returns pandas correctly.
    For ``ERROR``, ``message`` is ignored and ``GENERIC_ERROR_MESSAGE`` is stored.
    """
    status_path = path or STATUS_PATH
    payload = {
        "status": status,
        "message": _public_message(status, message),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    df = pd.DataFrame([payload])
    try:
        if storage.exists(status_path):
            storage.delete(status_path)
        storage.create(df, status_path)
        logger.info("Pipeline status: %s — %s", payload["status"], payload["message"])
    except Exception as exc:
        logger.warning("Failed to write pipeline status: %s", exc)


def set_error(storage: Any, *, path: Optional[str] = None) -> None:
    """Mark pipeline as Error with the generic user-facing message."""
    set_status(storage, ERROR, path=path)


def get_status(storage: Any, *, path: Optional[str] = None) -> dict:
    """Read current pipeline status from storage (always returns a plain dict)."""
    status_path = path or STATUS_PATH
    if not storage.exists(status_path):
        return dict(_IDLE)
    try:
        df = storage.read(status_path)
        if df is None or (hasattr(df, "empty") and df.empty):
            return dict(_IDLE)
        return _row_to_status(df)
    except Exception as exc:
        logger.warning("Failed to read pipeline status: %s", exc)
        return dict(_IDLE)
