"""Sensores simulados.

Cada sensor hace una caminata aleatoria acotada: el valor cambia poco entre
lecturas, como ocurre con un sensor real, y nunca sale de su rango.
"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorSpec:
    name: str        # se usa como último nivel del tópico
    unit: str
    minimum: float
    maximum: float
    step: float      # desviación típica del cambio entre lecturas
    decimals: int = 1


SENSORS: tuple[SensorSpec, ...] = (
    SensorSpec(name="temperatura", unit="°C", minimum=20.0, maximum=35.0, step=0.6),
    SensorSpec(name="humedad", unit="%", minimum=40.0, maximum=80.0, step=1.5),
    SensorSpec(name="presion", unit="hPa", minimum=1000.0, maximum=1025.0, step=0.8),
)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


class SimulatedSensor:
    def __init__(self, spec: SensorSpec, rng: random.Random | None = None) -> None:
        self.spec = spec
        self._rng = rng or random.Random()
        self._value = self._rng.uniform(spec.minimum, spec.maximum)

    def read(self) -> float:
        drift = self._rng.gauss(0, self.spec.step)
        self._value = clamp(self._value + drift, self.spec.minimum, self.spec.maximum)
        return round(self._value, self.spec.decimals)
