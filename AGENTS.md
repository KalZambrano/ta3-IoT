---
name: ta3-iot-mqtt
description: Guía para realizar la Tarea Académica 3 (IoT) de punta a punta: nodo simulado en Python que publica temperatura, humedad y presión con timestamp cada 5 s, broker EMQX en Docker con credenciales propias, verificación con MQTTX o MQTT Explorer, y visualización en Grafana (Telegraf + InfluxDB). Usar al implementar, probar, depurar o documentar este repositorio, o al redactar su informe técnico.
---

# TA3 · Simulación de flujo IoT con MQTT

## 1. Objetivo y alcance

Simular el flujo completo de un sistema IoT: **adquisición → transmisión → monitoreo**.

| Parte de la consigna | Qué se implementa |
|---|---|
| 1. Nodo IoT | `src/node.py` publica cada 5 s lecturas aleatorias con timestamp |
| 2. Broker | EMQX en Docker, con contraseña de administrador y usuario MQTT propios |
| 3. Verificación | MQTTX o MQTT Explorer suscrito a `iot/raspberrypi/temperatura` |
| Extensiones recomendadas | Timestamp, varios sensores y Grafana (incluidas) |

Fuera de alcance: TLS real, ACL por tópico y alta disponibilidad. Se mencionan en el informe como mejoras para producción.

## 2. Arquitectura

```
[Python: src/node.py] --MQTT 1883--> [EMQX] --+--> [MQTTX / MQTT Explorer]  (verificación manual)
   3 sensores, cada 5 s                       |
                                              +--> [Telegraf] --> [InfluxDB] --> [Grafana :3000]
```

- El nodo corre **en el host** (no en Docker) y se conecta a `localhost:1883`.
- Telegraf corre en Docker y se conecta a `emqx:1883` por la red interna de Compose.
- No se usa el plugin MQTT de Grafana porque solo muestra datos en vivo. InfluxDB guarda el historial, y eso permite graficar y documentar tendencias.

## 3. Contrato de datos

**Tópicos** (base configurable con `MQTT_TOPIC_BASE`):

- `iot/raspberrypi/temperatura` (tópico exigido por la consigna)
- `iot/raspberrypi/humedad`
- `iot/raspberrypi/presion`

**Mensaje** (un sensor por tópico, QoS 1):

```json
{
  "device_id": "raspberrypi-01",
  "sensor": "temperatura",
  "valor": 24.3,
  "unidad": "°C",
  "timestamp": "2026-10-10T15:30:00+00:00"
}
```

- `timestamp` es ISO 8601 en UTC. Telegraf lo usa como marca de tiempo del dato.
- Rangos simulados: temperatura 20–35 °C, humedad 40–80 %, presión 1000–1025 hPa.
- No cambiar nombres de campos ni de tópicos sin actualizar a la vez `telegraf/telegraf.conf` y `grafana/dashboards/iot-ta3.json`.

## 4. Estructura del repositorio

```
ta3-iot-mqtt/
├── SKILL.md                  # esta guía
├── README.md                 # arranque rápido
├── docker-compose.yml        # EMQX + InfluxDB + Telegraf + Grafana
├── .env.example              # plantilla de variables (el .env real no se commitea)
├── requirements.txt
├── src/
│   ├── config.py             # lee variables de entorno
│   ├── sensors.py            # sensores simulados (caminata aleatoria acotada)
│   ├── payload.py            # arma el JSON con timestamp
│   └── node.py               # conexión MQTT y bucle de publicación
├── tests/test_node.py        # pruebas unitarias
├── telegraf/telegraf.conf    # MQTT -> InfluxDB
├── grafana/
│   ├── provisioning/         # datasource y proveedor de dashboards
│   └── dashboards/iot-ta3.json
└── docs/
    ├── informe-tecnico.md    # plantilla del informe
    └── evidencias/           # capturas numeradas
```

## 5. Convenciones

- Python 3.10 o superior, entorno virtual `.venv`, dependencias solo en `requirements.txt` (pip). La regla de pnpm/Bun aplica a proyectos JavaScript, no a este.
- Una responsabilidad por módulo. Sin valores fijos en el código: todo lo configurable va en `.env`.
- Nombres en `snake_case` para archivos y funciones, `PascalCase` para clases. Comentarios solo donde explican una decisión, no lo que el código ya dice.
- Nunca commitear `.env`, contraseñas ni tokens.
- Commits pequeños, estilo convencional: `chore: bootstrap`, `feat: nodo publica temperatura`, `docs: capturas de la fase 4`. El primer commit es solo el esqueleto.

## 6. Flujo de trabajo por fases

Cada fase termina con una **comprobación** y una **evidencia** (captura en `docs/evidencias/` con nombre `NN-descripcion.png`).

### Fase 0 · Prerrequisitos

1. Instalar Python 3.10+, VS Code, Docker Desktop (en Windows requiere WSL2) y MQTTX o MQTT Explorer.
2. Verificar: `python --version`, `docker --version`, `docker compose version`.
3. Revisar que los puertos **1883, 18083, 8086 y 3000** estén libres.

Evidencia: `01-versiones.png`.

### Fase 1 · Entorno y secretos

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # Windows: copy .env.example .env
```

Editar `.env` y reemplazar **todas** las claves `cambia-...` por valores propios. `INFLUX_TOKEN` debe ser largo y aleatorio.

Comprobación: `python -m unittest discover -s tests -t .` termina en `OK`.

### Fase 2 · Broker EMQX (Parte 2)

```bash
docker compose up -d emqx
docker compose ps          # emqx debe aparecer "healthy"
```

1. Abrir `http://localhost:18083` e iniciar sesión con `EMQX_DASHBOARD_USER` y `EMQX_DASHBOARD_PASSWORD`.
2. Si ya habías levantado EMQX antes con otra clave, esa clave quedó guardada en el volumen. Cambiarla desde el dashboard (menú del usuario > Cambiar contraseña) o ejecutar `docker compose down -v` para empezar de cero.

Comprobación: el dashboard abre y el puerto 1883 aparece como listener activo (Management > Listeners).
Evidencias: `02-docker-compose-ps.png`, `03-emqx-dashboard.png`, `04-emqx-listeners.png`.

### Fase 3 · Credenciales MQTT

Por defecto EMQX acepta conexiones anónimas. Para exigir credenciales:

1. Dashboard > **Access Control > Authentication > Create**.
2. Mecanismo **Password-Based**, backend **Built-in Database**, identificar por **username**.
3. Entrar al autenticador creado > **Users > Add** y registrar `MQTT_USERNAME` y `MQTT_PASSWORD` del `.env`.

Comprobación: en MQTTX, conectar sin usuario debe fallar y conectar con usuario y clave debe funcionar.
Evidencias: `05-autenticacion-emqx.png`, `06-conexion-rechazada.png`.

### Fase 4 · Nodo Python (Parte 1)

```bash
python -m src.node
```

Debe aparecer `Conectado al broker MQTT` y, cada 5 s, tres líneas `iot/raspberrypi/... -> {...}`. Si el broker aún no está arriba, el nodo reintenta solo. Detener con Ctrl+C.

Comprobación: salida continua, sin errores, con timestamp en cada mensaje.
Evidencia: `07-nodo-publicando.png`.

### Fase 5 · Verificación con cliente MQTT (Parte 3)

En MQTTX o MQTT Explorer:

1. Nueva conexión: host `localhost`, puerto `1883`, usuario y clave de la Fase 3.
2. Suscribirse a `iot/raspberrypi/temperatura`. Después, para ver todo, a `iot/raspberrypi/#`.
3. Confirmar que llega un mensaje cada ~5 s y que el JSON coincide con lo que imprime el nodo.

Comprobación: los valores y timestamps de la terminal coinciden con los del cliente.
Evidencias: `08-mqttx-suscripcion.png`, `09-mqttx-mensajes.png`.

### Fase 6 · Grafana (extensión)

```bash
docker compose up -d
docker compose ps          # los 4 servicios en "running"
docker compose logs telegraf --tail 20
```

1. Con el nodo corriendo, abrir `http://localhost:3000` (usuario y clave de `GRAFANA_*`).
2. Ir a **Dashboards > IoT > IoT TA3 - Sensores Raspberry Pi**.
3. Esperar 15–30 s. Deben moverse los tres indicadores y las tres series.

Comprobación: los paneles se actualizan solos cada 5 s.
Evidencias: `10-docker-compose-completo.png`, `11-grafana-dashboard.png`.

### Fase 7 · Informe técnico

Completar `docs/informe-tecnico.md` con las capturas de `docs/evidencias/`. Reglas:

- Redactar con palabras propias, en español académico simple y oraciones cortas, evitando subordinadas largas. La rúbrica premia el análisis reflexivo, y el reglamento sanciona la copia.
- Documentar **todos** los errores reales que aparezcan: síntoma, causa, solución. Es un criterio explícito de la consigna.
- Incluir una sección de mejoras para producción: TLS en el puerto 8883, ACL por tópico, un usuario MQTT por dispositivo y secretos fuera del repositorio.

### Fase 8 · Entrega

Comprimir el repositorio sin `.env` ni `.venv`. Nombrar el archivo según lo pida el docente (por ejemplo `TA3_Apellido_Nombre.zip`). Revisar la rúbrica de la sección 8 antes de subirlo.

## 7. Comandos útiles

| Acción | Comando |
|---|---|
| Levantar todo | `docker compose up -d` |
| Estado | `docker compose ps` |
| Logs de un servicio | `docker compose logs -f emqx` |
| Reiniciar un servicio | `docker compose restart telegraf` |
| Apagar conservando datos | `docker compose down` |
| Apagar y borrar datos | `docker compose down -v` |
| Pruebas | `python -m unittest discover -s tests -t .` |

## 8. Mapeo con la rúbrica

| Criterio (nivel máximo) | Evidencia en este repositorio |
|---|---|
| Nodo IoT en Python | Código modular y comentado, salida continua sin errores (`07`), pruebas unitarias |
| Broker EMQX | Configuración completa con credenciales personalizadas (`03`, `05`) |
| Verificación con cliente MQTT | Datos consistentes y documentados (`08`, `09`) más contraste con Grafana (`11`) |
| Informe técnico | `docs/informe-tecnico.md` completo, con errores y reflexión |
| Presentación de entregables | Estructura de carpetas, nombres claros, capturas numeradas |

## 9. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `docker compose up` falla con `Define ... en .env` | Falta una variable | Completar `.env` a partir de `.env.example` |
| Contraseña del dashboard no funciona | El volumen conserva la clave del primer arranque | Cambiarla en el dashboard o `docker compose down -v` |
| El nodo muestra `not currently connected` | Broker apagado o puerto ocupado | `docker compose ps`; revisar el puerto 1883 |
| El nodo no conecta y el broker está arriba | Usuario no creado, o `.env` distinto al de EMQX | Repetir Fase 3 y comparar `MQTT_USERNAME` y `MQTT_PASSWORD` |
| MQTTX no recibe nada | Tópico mal escrito o suscripción sin permisos | Probar `iot/raspberrypi/#` |
| Grafana sin datos | Telegraf sin credenciales o sin conexión | `docker compose logs telegraf`; luego `docker compose restart telegraf` |
| Telegraf: `not authorized` | Usuario MQTT no creado en EMQX | Crearlo (Fase 3) y reiniciar Telegraf |
| Datos en Grafana con hora distinta | Zona horaria | Los timestamps son UTC; el dashboard usa la hora del navegador |
| Docker no inicia en Windows | WSL2 desactivado | Activar WSL2 / virtualización en BIOS |

## 10. Definición de terminado

- [ ] Pruebas unitarias en `OK`.
- [ ] `docker compose ps` con los 4 servicios activos.
- [ ] Contraseña de administrador de EMQX personalizada y usuario MQTT creado.
- [ ] El nodo publica cada 5 s con timestamp, sin errores.
- [ ] MQTTX o MQTT Explorer recibe `iot/raspberrypi/temperatura` en tiempo real.
- [ ] Grafana muestra los tres sensores actualizándose.
- [ ] Capturas `01` a `11` en `docs/evidencias/`.
- [ ] Informe completo, con errores encontrados y reflexión propia.
- [ ] `.env` ausente del repositorio y de la entrega.

## 11. Reglas para el agente que use esta guía

- Seguir las fases en orden. Si falta información (por ejemplo, el `docker-compose.yml` del docente), pedirla y no inventarla.
- Si el docente entrega su propio `docker-compose.yml`, conservar su servicio `emqx` tal cual y agregar solo `influxdb`, `telegraf` y `grafana` del compose de este repositorio.
- No cambiar el tópico `iot/raspberrypi/temperatura` ni el intervalo de 5 s.
- No escribir secretos en el código ni en la documentación.
- No redactar el informe completo en lugar del estudiante: proponer estructura, revisar y corregir lo que él escriba.
- Probar antes de afirmar. Si algo no se pudo ejecutar, decirlo.
