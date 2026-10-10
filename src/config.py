"""Configuración del nodo IoT, leída desde variables de entorno (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    mqtt_host: str
    mqtt_port: int
    mqtt_username: str | None
    mqtt_password: str | None
    topic_base: str
    device_id: str
    publish_interval_seconds: float

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            mqtt_host=os.getenv("MQTT_HOST", "localhost"),
            mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
            mqtt_username=os.getenv("MQTT_USERNAME") or None,
            mqtt_password=os.getenv("MQTT_PASSWORD") or None,
            topic_base=os.getenv("MQTT_TOPIC_BASE", "iot/raspberrypi"),
            device_id=os.getenv("DEVICE_ID", "raspberrypi-01"),
            publish_interval_seconds=float(os.getenv("PUBLISH_INTERVAL_SECONDS", "5")),
        )
