# 🏭 SCADA Industrial IoT - Sistema de Monitoreo y Control Distribuido

Este proyecto implementa un sistema **SCADA (Supervisory Control and Data Acquisition)** híbrido y escalable. Integra dispositivos de borde (ESP32) con un Gateway local (Raspberry Pi) y almacenamiento en la nube (InfluxDB Cloud), permitiendo la supervisión en tiempo real, control de actuadores y gestión de alarmas críticas vía Telegram.

![Dashboard Preview](assets/dashboard_preview.png)
*(Reemplaza esto con una captura de tu dashboard)*

## 📋 Características Principales

### 📡 Adquisición de Datos (Data Acquisition)
* **Simulación de Maquinaria:** Firmware en ESP32 capaz de simular múltiples máquinas industriales con comportamientos físicos (inercia térmica, vibración senoidal y ruido estático).
* **Flota Dinámica:** Soporte para *n* máquinas simultáneas. El sistema detecta y registra automáticamente nuevas máquinas añadidas a la red.
* **Buffer Circular:** Monitor de tráfico "Raw" en tiempo real para depuración de paquetes JSON.

### 👁️ Supervisión (Supervisory)
* **Dashboard Web Moderno:** Interfaz oscura (Dark Mode) construida con Bootstrap 5 y ApexCharts.
* **Visualización en Tiempo Real:** Gráficas de tendencia limpias (sin ruido visual) para Temperatura y Vibración.
* **KPIs en Vivo:** Indicadores numéricos instantáneos.
* **Monitor de Salud del Servidor:** Visualización de uso de CPU, RAM, Disco y Temperatura de la Raspberry Pi.

### 🎮 Control
* **Control Bidireccional:** Ajuste de la frecuencia de muestreo de los sensores (ESP32) desde la interfaz web (de 200ms a 5 minutos).
* **Gestión de Alarmas:** Configuración de umbrales (Setpoints) de temperatura y vibración independientes por máquina.

### 🔔 Notificaciones y Reportes
* **Integración con Telegram:** Bot de alertas en tiempo real con lógica *anti-spam* (Cool-down de 60s).
* **Exportación de Datos:** Generación de reportes históricos en formato `.csv` (Excel) directamente desde el navegador.

---

## 🏗️ Arquitectura del Sistema

El flujo de datos sigue una arquitectura **Edge-to-Cloud**:

1.  **Edge (ESP32):** Genera datos y recibe comandos de configuración.
2.  **Gateway (Raspberry Pi):** * Recibe datos vía HTTP POST.
    * Procesa lógica de negocio (Alarmas).
    * Aloja el Servidor Web (Flask).
    * Envía datos a la nube.
3.  **Cloud (InfluxDB AWS):** Base de datos de series de tiempo para persistencia histórica.
4.  **Client (Navegador):** Visualización y Control.

---

## 🛠️ Tecnologías Utilizadas

* **Hardware:**
    * Espressif ESP32 (DevKit V1)
    * Raspberry Pi 3B+/4 (Gateway)
* **Backend & Gateway:**
    * Python 3.x
    * Flask (Microframework Web)
    * InfluxDB Client
    * PSUtil (Monitor de sistema)
* **Frontend:**
    * HTML5 / CSS3 / JavaScript
    * Bootstrap 5 (UI Kit)
    * ApexCharts.js (Visualización de datos)
    * FontAwesome (Iconografía)
* **Firmware:**
    * C++ / Arduino Framework
    * ArduinoJson v6
    * HTTPClient
* **Servicios Externos:**
    * InfluxDB Cloud (AWS region us-east-1)
    * Telegram Bot API

---

## 🚀 Instalación y Configuración

### 1. Configuración del Gateway (Raspberry Pi)

Clonar el repositorio y crear un entorno virtual:

```bash
git clone [https://github.com/tu-usuario/scada-iot.git](https://github.com/tu-usuario/scada-iot.git)](https://github.com/RafaelTorresCH/Supervisory-Control-And-Data-Acquisition.git)
cd scada-iot
python3 -m venv venv
source venv/bin/activate
