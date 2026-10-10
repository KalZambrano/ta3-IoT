"""Construcción del mensaje JSON que se publica en cada tópico."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .sensors import SensorSpec


def build_payload(
    device_id: str,
    spec: SensorSpec,
    value: float,
    now: datetime | None = None,
) -> dict[str, Any]:
    moment = now or datetime.now(timezone.utc)
    return {
        "device_id": device_id,
        "sensor": spec.name,
        "valor": value,
        "unidad": spec.unit,
        "timestamp": moment.isoformat(timespec="seconds"),
    }


def to_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)
