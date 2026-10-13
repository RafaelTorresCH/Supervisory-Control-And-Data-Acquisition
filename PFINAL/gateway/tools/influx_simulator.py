import time
import random
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN ---
# Reemplaza con tus datos reales de InfluxDB
TOKEN = "xtQiDZLYWisYfZU7sg37ZjC6uKHw737Ol52dobHg7xaQyLoCYAqk7Lu7NfyVmnBhWhnL6lYmHmmRMWMkDEo5wA=="
ORG = "rasp"
BUCKET = "DT_RASP"
URL = "https://us-east-1-1.aws.cloud2.influxdata.com"

def main():
    # 1. Crear el cliente
    # El cliente maneja la conexión HTTP y la autenticación
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)

    # 2. Configurar la API de escritura
    # SYNCHRONOUS: El script espera a que Influx confirme la recepción (bueno para debug)
    # ASYNCHRONOUS: El script no espera (mejor para alto rendimiento/batching)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print("Iniciando envío de datos simulados... (Ctrl+C para detener)")

    try:
        while True:
            # 3. Simulación de datos (ej. un sensor de temperatura oscilando)
            # Generamos un valor float aleatorio entre 20.0 y 25.0
            temperatura = 22.5 + random.uniform(-2.5, 2.5)
            
            # 4. Construcción del Punto (Data Point)
            # Measurement: El nombre de la "tabla" o medición (ej. "sensores_planta")
            # Tag: Metadatos indexados para filtrar rápido (ej. ID del sensor, ubicación)
            # Field: El valor real a graficar (no indexado por defecto)
            p = Point("sensores_planta") \
                .tag("ubicacion", "laboratorio_1") \
                .tag("id_sensor", "temp_001") \
                .field("temperatura_celsius", temperatura)

            # 5. Escribir en el Bucket
            write_api.write(bucket=BUCKET, org=ORG, record=p)

            print(f"Dato enviado: {temperatura:.2f} °C")
            
            # Esperar 1 segundo antes del siguiente dato
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo simulación...")
    except Exception as e:
        print(f"\nError crítico: {e}")
    finally:
        # Cerrar conexión limpiamente
        client.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()