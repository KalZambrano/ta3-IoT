"""Pruebas unitarias del generador de lecturas y del payload.

Ejecutar desde la raíz: python -m unittest discover -s tests -t .
"""
import json
import random
import unittest
from datetime import datetime, timezone

from src.payload import build_payload, to_json
from src.sensors import SENSORS, SimulatedSensor


class SimulatedSensorTest(unittest.TestCase):
    def test_values_stay_within_range(self) -> None:
        for spec in SENSORS:
            sensor = SimulatedSensor(spec, random.Random(42))
            for _ in range(500):
                value = sensor.read()
                self.assertGreaterEqual(value, spec.minimum)
                self.assertLessEqual(value, spec.maximum)


class PayloadTest(unittest.TestCase):
    def test_payload_contains_required_fields(self) -> None:
        spec = SENSORS[0]
        moment = datetime(2026, 10, 10, 15, 30, 0, tzinfo=timezone.utc)
        payload = json.loads(to_json(build_payload("raspberrypi-01", spec, 24.3, moment)))
        self.assertEqual(payload["device_id"], "raspberrypi-01")
        self.assertEqual(payload["sensor"], "temperatura")
        self.assertEqual(payload["valor"], 24.3)
        self.assertEqual(payload["unidad"], "°C")
        self.assertEqual(payload["timestamp"], "2026-10-10T15:30:00+00:00")

    def test_timestamp_is_parseable(self) -> None:
        payload = build_payload("raspberrypi-01", SENSORS[1], 55.0)
        parsed = datetime.fromisoformat(payload["timestamp"])
        self.assertIsNotNone(parsed.tzinfo)


if __name__ == "__main__":
    unittest.main()
