# Informe técnico · Tarea Académica N° 3

**Curso:** [completar]
**Integrante(s):** [completar]
**Fecha:** [completar]

## 1. Introducción y objetivo

[Explica en 4 a 6 oraciones qué es MQTT, qué papel cumple un broker y qué lograste simular.]

## 2. Arquitectura

[Inserta el diagrama o descríbelo: nodo Python, EMQX, cliente MQTT, Telegraf, InfluxDB y Grafana. Explica qué hace cada pieza.]

## 3. Procedimiento

### 3.1 Parte 1: nodo IoT en Python
[Describe cómo generas los valores, el formato JSON, el timestamp y el intervalo de 5 s.]
Evidencia: `evidencias/07-nodo-publicando.png`

### 3.2 Parte 2: broker EMQX
[Describe la instalación de Docker, el docker-compose.yml, el cambio de contraseña y la creación del usuario MQTT.]
Evidencias: `evidencias/02` a `evidencias/06`

### 3.3 Parte 3: verificación con cliente MQTT
[Describe la conexión, la suscripción a iot/raspberrypi/temperatura y lo que observaste.]
Evidencias: `evidencias/08`, `evidencias/09`

### 3.4 Extensión: visualización en Grafana
[Describe el flujo Telegraf, InfluxDB y Grafana, y qué muestra el dashboard.]
Evidencias: `evidencias/10`, `evidencias/11`

## 4. Resultados

[Presenta una tabla corta con algunos mensajes recibidos y compara terminal, cliente MQTT y Grafana.]

## 5. Errores encontrados y soluciones

| Error o síntoma | Causa | Solución |
|---|---|---|
| [completar] | [completar] | [completar] |

## 6. Análisis y reflexión

[Responde con tus palabras: ¿por qué conviene un broker entre el nodo y los consumidores? ¿Qué ventaja tiene publicar un sensor por tópico? ¿Qué cambia entre ver datos en vivo y guardarlos en una base de datos?]

## 7. Mejoras para producción

- TLS en el puerto 8883 con certificados propios.
- Un usuario MQTT por dispositivo y ACL por tópico.
- Secretos fuera del repositorio.
- [Agrega las que propongas tú.]

## 8. Conclusiones

[3 a 5 oraciones.]

## Referencias

[EMQX, MQTT.org, Grafana, InfluxDB, Telegraf: agrega las URLs que consultaste.]
