"""Pipeline status registry written to storage for API / UI consumption."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

STATUS_PATH = "pipeline_status.json"

IDLE = "Idle"
BUILDING = "Building"
WARNING = "Warning"
ERROR = "Error"
READY = "Ready"


def set_status(storage: Any, status: str, message: str) -> None:
    """Overwrite the current pipeline status in storage."""
    payload = {
        "status": status,
        "message": message,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        storage.create(payload, STATUS_PATH)
        logger.info("Pipeline status: %s — %s", status, message)
    except Exception as exc:
        logger.warning("Failed to write pipeline status: %s", exc)


def get_status(storage: Any) -> dict:
    """Read the current pipeline status from storage."""
    if not storage.exists(STATUS_PATH):
        return {
            "status": IDLE,
            "message": "No pipeline run yet",
            "updated_at": None,
        }
    try:
        with open(storage.get_path(STATUS_PATH), encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "status" in data:
            return data
    except Exception as exc:
        logger.warning("Failed to read pipeline status: %s", exc)
    return {
        "status": IDLE,
        "message": "No pipeline run yet",
        "updated_at": None,
    }
