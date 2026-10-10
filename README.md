# TA3 · Flujo IoT con MQTT, EMQX y Grafana

Simulación de un flujo IoT: un nodo en Python publica temperatura, humedad y presión con timestamp cada 5 segundos. EMQX distribuye los mensajes, y Grafana los muestra con Telegraf e InfluxDB.

```
Python (host) --> EMQX :1883 --> MQTTX / MQTT Explorer
                       |
                       +--> Telegraf --> InfluxDB --> Grafana :3000
```

La guía completa, paso a paso, está en [`SKILL.md`](SKILL.md).

## Arranque rápido

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
# Editar .env y cambiar todas las claves "cambia-..."

docker compose up -d emqx          # 1. broker
# 2. Crear el usuario MQTT en http://localhost:18083 (SKILL.md, Fase 3)
docker compose up -d               # 3. resto de servicios
python -m src.node                 # 4. nodo publicando
```

## Accesos

| Servicio | URL |
|---|---|
| EMQX Dashboard | http://localhost:18083 |
| Grafana | http://localhost:3000 |
| InfluxDB | http://localhost:8086 |
| MQTT | `localhost:1883` |

## Pruebas

```bash
python -m unittest discover -s tests -t .
```

## Notas

- Si el docente entrega su propio `docker-compose.yml`, conserva su servicio `emqx` y agrega los demás servicios de este.
- El puerto 8883 (TLS) queda expuesto, pero sin certificados configurados. Activar TLS se documenta como mejora para producción.
- `.env` contiene secretos y no se versiona.
