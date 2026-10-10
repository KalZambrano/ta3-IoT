"""Nodo IoT simulado: publica lecturas de sensores al broker MQTT.

Ejecutar desde la raíz del repositorio:
    python -m src.node
"""
from __future__ import annotations

import logging
import threading
import time

import paho.mqtt.client as mqtt

from .config import Settings
from .payload import build_payload, to_json
from .sensors import SENSORS, SimulatedSensor

logger = logging.getLogger("nodo-iot")


def on_connect(client, userdata, flags, reason_code, properties) -> None:
    if reason_code.is_failure:
        logger.error("Conexión rechazada por el broker: %s", reason_code)
        return
    logger.info("Conectado al broker MQTT")
    userdata.set()


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties) -> None:
    logger.warning("Desconectado del broker (%s). Reintentando...", reason_code)


def create_client(settings: Settings, connected: threading.Event) -> mqtt.Client:
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"{settings.device_id}-publisher",
        userdata=connected,
    )
    if settings.mqtt_username:
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    return client


def publish_readings(
    client: mqtt.Client,
    settings: Settings,
    sensors: list[SimulatedSensor],
) -> None:
    for sensor in sensors:
        topic = f"{settings.topic_base}/{sensor.spec.name}"
        payload = to_json(build_payload(settings.device_id, sensor.spec, sensor.read()))
        result = client.publish(topic, payload, qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.warning("No se pudo publicar en %s: %s", topic, mqtt.error_string(result.rc))
            continue
        logger.info("%s -> %s", topic, payload)


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    settings = Settings.from_env()
    sensors = [SimulatedSensor(spec) for spec in SENSORS]
    connected = threading.Event()
    client = create_client(settings, connected)

    # connect_async + loop_start: el cliente sigue intentando aunque el broker
    # todavía no esté levantado.
    client.connect_async(settings.mqtt_host, settings.mqtt_port, keepalive=60)
    client.loop_start()
    if not connected.wait(timeout=10):
        logger.warning("Sin conexión al broker tras 10 s; se seguirá reintentando")
    logger.info(
        "Publicando cada %ss en %s:%s (Ctrl+C para detener)",
        settings.publish_interval_seconds,
        settings.mqtt_host,
        settings.mqtt_port,
    )

    try:
        while True:
            publish_readings(client, settings, sensors)
            time.sleep(settings.publish_interval_seconds)
    except KeyboardInterrupt:
        logger.info("Nodo detenido por el usuario")
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    run()
