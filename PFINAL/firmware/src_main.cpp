#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> 

// ==========================================
// 1. CONFIGURACIÓN DE RED
// ==========================================
const char* WIFI_SSID = "MOVISTAR_2157";
const char* WIFI_PASS = "Ui242tcBrvdUkchsxfrH";

// IP de tu Raspberry Pi
const char* SERVER_URL = "http://192.168.20.26:5000/api/telemetria";

// ==========================================
// 2. VARIABLES GLOBALES DEL SISTEMA
// ==========================================
int intervalo_envio = 1000;  
unsigned long last_time = 0;

// Configuración de Simulación
int cantidad_maquinas = 1;   
int modo_simulacion = 1;     

// Variables para simulación física
float tiempo_simulado = 0.0;

// ==========================================
// 3. PROTOTIPOS DE FUNCIONES (SOLUCIÓN AL ERROR)
// ==========================================
void enviarDatos();
void verificarComandosSerial();
void mostrarMenu();

// ==========================================
// SETUP
// ==========================================
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50); 

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("\nConectando WiFi");
  while(WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi OK - IP: " + WiFi.localIP().toString());

  mostrarMenu(); // Ahora sí funciona porque ya declaramos la función arriba
}

// ==========================================
// LOOP PRINCIPAL
// ==========================================
void loop() {
  verificarComandosSerial();

  if (millis() - last_time > intervalo_envio) {
    last_time = millis();
    tiempo_simulado += 0.1; 

    if (WiFi.status() == WL_CONNECTED) {
      enviarDatos();
    } else {
      Serial.println("Error: WiFi desconectado");
      WiFi.reconnect();
    }
  }
}

// ==========================================
// FUNCIONES AUXILIARES
// ==========================================

void enviarDatos() {
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // Aumentamos buffer para soportar muchas máquinas
  DynamicJsonDocument doc(8192); 
  
  JsonArray arrayDatos = doc.to<JsonArray>();

  for (int i = 1; i <= cantidad_maquinas; i++) {
    JsonObject obj = arrayDatos.createNestedObject();
    obj["id"] = "MAQ_" + String(i);
    
    float temp = 0.0;
    float vib = 0.0;

    if (modo_simulacion == 1) { 
      // MODO ESTABLE
      temp = 50.0 + (10.0 * sin(tiempo_simulado + (i * 1.5))) + random(-10, 10)/10.0;
      vib = 1.5 + (0.5 * cos(tiempo_simulado)) + random(0, 5)/10.0;
    } else {
      // MODO ALEATORIO
      temp = random(200, 900) / 10.0; 
      vib = random(0, 100) / 10.0;    
    }

    obj["temperatura"] = temp;
    obj["vibracion"] = vib;
  }

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  int httpCode = http.POST(jsonPayload);

  if (httpCode == 200) {
    String response = http.getString();
    
    StaticJsonDocument<200> respDoc;
    DeserializationError error = deserializeJson(respDoc, response);

    if (!error) {
      int nuevo_tiempo = respDoc["nuevo_intervalo"];
      if (nuevo_tiempo >= 200 && nuevo_tiempo != intervalo_envio) {
        intervalo_envio = nuevo_tiempo;
        Serial.printf("⚡ COMANDO RECIBIDO: Velocidad actualizada a %d ms\n", intervalo_envio);
      }
    }
  } else {
    Serial.printf("Error HTTP: %d\n", httpCode);
  }
  
  http.end();
}

void verificarComandosSerial() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim(); 
    comando.toUpperCase(); 

    if (comando.startsWith("C=")) {
      int val = comando.substring(2).toInt();
      if (val > 0 && val <= 30) {
        cantidad_maquinas = val;
        Serial.printf(">> Configuración: Simulando %d máquinas.\n", cantidad_maquinas);
      } else {
        Serial.println(">> Error: Cantidad debe ser entre 1 y 30.");
      }
    }
    else if (comando.startsWith("M=")) {
      int val = comando.substring(2).toInt();
      if (val == 1 || val == 2) {
        modo_simulacion = val;
        String m = (modo_simulacion == 1) ? "ESTABLE" : "ALEATORIO";
        Serial.println(">> Configuración: Modo " + m);
      } else {
        Serial.println(">> Error: Use M=1 (Estable) o M=2 (Aleatorio)");
      }
    }
    else {
      mostrarMenu();
    }
  }
}

void mostrarMenu() {
  Serial.println("\n--- CONSOLA DE CONTROL ESP32 ---");
  Serial.println("Comandos disponibles:");
  Serial.println("  C=X  -> Cambiar cantidad de máquinas (Ej: C=5)");
  Serial.println("  M=1  -> Modo ESTABLE");
  Serial.println("  M=2  -> Modo ALEATORIO");
  Serial.println("--------------------------------");
  Serial.printf("ACTUAL: %d Máquinas | Modo %d | Intervalo %d ms\n", cantidad_maquinas, modo_simulacion, intervalo_envio);
}