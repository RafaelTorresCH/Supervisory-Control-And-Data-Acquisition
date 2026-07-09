# SCADA Industrial IoT - Distributed Monitoring and Control System

This project implements a hybrid and scalable SCADA (Supervisory Control and Data Acquisition) system. It integrates edge devices (ESP32) with a local Gateway (Raspberry Pi) and cloud storage (InfluxDB Cloud), enabling real-time supervision, actuator control, and critical alarm management via Telegram.


## Main Features

### Data Acquisition
* **Machinery Simulation:** ESP32 firmware capable of simulating multiple industrial machines with physical behaviors (thermal inertia, sinusoidal vibration, and static noise).
* **Dynamic Fleet:** Support for n simultaneous machines. The system automatically detects and registers new machines added to the network.
* **Circular Buffer:** Real-time Raw traffic monitor for JSON packet debugging.

### Supervision
* **Modern Web Dashboard:** Dark Mode interface built with Bootstrap 5 and ApexCharts.
* **Real-Time Visualization:** Clean trend charts (without visual noise) for Temperature and Vibration.
* **Live KPIs:** Instant numerical indicators.
* **Server Health Monitor:** Visualization of CPU, RAM, Disk, and Temperature usage of the Raspberry Pi.

### Control
* **Bidirectional Control:** Adjustment of the sensor sampling frequency (ESP32) from the web interface (from 200ms to 5 minutes).
* **Alarm Management:** Independent configuration of temperature and vibration thresholds (Setpoints) per machine.

### Notifications and Reports
* **Telegram Integration:** Real-time alerts bot with anti-spam logic (60s Cool-down).
* **Data Export:** Generation of historical reports in .csv format (Excel) directly from the browser.

---

## System Architecture

The data flow follows an Edge-to-Cloud architecture:

1. Edge (ESP32): Generates data and receives configuration commands.
2. Gateway (Raspberry Pi):
    * Receives data via HTTP POST.
    * Processes business logic (Alarms).
    * Hosts the Web Server (Flask).
    * Sends data to the cloud.
3. Cloud (InfluxDB AWS): Time series database for historical persistence.
4. Client (Browser): Visualization and Control.

---

## Technologies Used

* **Hardware:**
    * Espressif ESP32 (DevKit V1)
    * Raspberry Pi 3B+/4 (Gateway)
* **Backend & Gateway:**
    * Python 3.x
    * Flask (Web Microframework)
    * InfluxDB Client
    * PSUtil (System monitor)
* **Frontend:**
    * HTML5 / CSS3 / JavaScript
    * Bootstrap 5 (UI Kit)
    * ApexCharts.js (Data visualization)
    * FontAwesome (Iconography)
* **Firmware:**
    * C++ / Arduino Framework
    * ArduinoJson v6
    * HTTPClient
* **External Services:**
    * InfluxDB Cloud (AWS region us-east-1)
    * Telegram Bot API

---

## Installation and Configuration

### 1. Gateway Configuration (Raspberry Pi)

Clone the repository and create a virtual environment:

```bash
git clone [https://github.com/RafaelTorresCH/Supervisory-Control-And-Data-Acquisition.git](https://github.com/RafaelTorresCH/Supervisory-Control-And-Data-Acquisition.git)
cd scada-iot
python3 -m venv venv
source venv/bin/activate
