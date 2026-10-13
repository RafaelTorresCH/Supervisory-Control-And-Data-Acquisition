# Gateway

Servidor Flask que centraliza la recepción, procesamiento y visualización de
la telemetría enviada por los ESP32.

## Archivos

- `app.py`: aplicación principal del gateway.
- `tools/influx_simulator.py`: herramienta auxiliar para generar datos de
  prueba directamente en InfluxDB.

## Ejecución

Instala las dependencias del proyecto en un entorno virtual y ejecuta:

```bash
python app.py
```

La configuración de red, InfluxDB y Telegram debe revisarse antes de iniciar
el servicio en la Raspberry Pi.
