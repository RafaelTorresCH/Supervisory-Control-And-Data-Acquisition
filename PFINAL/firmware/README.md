# Firmware ESP32

Proyecto PlatformIO del simulador de máquinas industriales. El firmware genera
telemetría, la envía al gateway mediante HTTP y recibe comandos para ajustar
la simulación y el intervalo de envío.

## Uso

Ejecuta los comandos desde esta carpeta:

```bash
pio run
pio run --target upload
pio device monitor
```

Antes de cargar el firmware, revisa en `src/main.cpp` la red Wi-Fi y la URL del
gateway correspondiente al entorno de prueba.
