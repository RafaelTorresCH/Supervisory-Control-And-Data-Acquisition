# SCADA Industrial IoT

Implementación final del sistema SCADA distribuido para supervisión y control
de máquinas industriales simuladas.

## Estructura del proyecto

```text
PFINAL/
├── docs/
│   └── architecture.md       # Arquitectura, diagramas y plan de verificación
├── firmware/                  # Proyecto PlatformIO para el ESP32
│   ├── platformio.ini
│   └── src/
│       └── main.cpp
└── gateway/                   # Servidor Flask para la Raspberry Pi
    ├── app.py                # API, dashboard y lógica del gateway
    └── tools/
        └── influx_simulator.py # Generador independiente de datos para pruebas
```

## Componentes

### Gateway — Raspberry Pi

`gateway/app.py` contiene el servidor Flask, el dashboard web, la recepción de
telemetría, la escritura en InfluxDB, la gestión de alarmas y los comandos
enviados al ESP32.

Para ejecutar el gateway:

```bash
cd gateway
python app.py
```

El simulador de InfluxDB es una herramienta independiente para pruebas:

```bash
python tools/influx_simulator.py
```

### Firmware — ESP32

`firmware/` es un proyecto PlatformIO. Ábrelo desde PlatformIO o ejecútalo
desde esa carpeta:

```bash
cd firmware
pio run
pio run --target upload
pio device monitor
```

## Documentación

La descripción técnica, los diagramas de arquitectura y el plan de verificación
se encuentran en [docs/architecture.md](docs/architecture.md).

## Configuración

Antes de desplegar el sistema, revisa las credenciales de red, la URL del
gateway y la configuración de InfluxDB. No publiques credenciales reales en el
repositorio; utiliza variables de entorno o un archivo local excluido de Git
para un despliegue real.
