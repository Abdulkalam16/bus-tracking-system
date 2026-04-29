#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>

// ---------- CONFIG ----------

// WiFi
const char* ssid = "your wifi name ";
const char* password = "your password";

// Bus ID 
String BUS_ID = "NEC-01";

// Change this to your PC IP
String SERVER_URL = "http://YOUR_LOCAL_IP:5000/api/update_location";

// Update interval
unsigned long UPDATE_INTERVAL = 5000;


// ---------- GPS ----------
TinyGPSPlus gps;
SoftwareSerial gpsSerial(D5, D6);  // RX, TX


// ---------- WiFi ----------
WiFiClient client;

unsigned long lastUpdate = 0;


void setup() {

  Serial.begin(115200);
  gpsSerial.begin(9600);

  Serial.println();
  Serial.println("NEC-01 Bus Tracker Starting...");

  connectWiFi();
}


void loop() {

  // Read GPS
  while (gpsSerial.available()) {
    gps.encode(gpsSerial.read());
  }

  // Send every 5 seconds
  if (millis() - lastUpdate > UPDATE_INTERVAL) {

    if (gps.location.isValid()) {

      float lat = gps.location.lat();
      float lng = gps.location.lng();

      Serial.println("GPS OK");
      Serial.print("Lat: "); Serial.println(lat);
      Serial.print("Lng: "); Serial.println(lng);

      sendLocation(lat, lng);

    } else {
      Serial.println("Waiting for GPS...");
    }

    lastUpdate = millis();
  }
}


// ---------- WiFi ----------
void connectWiFi() {

  Serial.print("Connecting WiFi");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}


// ---------- Send Location ----------
void sendLocation(float lat, float lng) {

  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
    return;
  }

  HTTPClient http;

  http.begin(client, SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // JSON for your Flask API
  String json = "{";
  json += "\"bus_id\":\"" + BUS_ID + "\",";
  json += "\"latitude\":" + String(lat, 6) + ",";
  json += "\"longitude\":" + String(lng, 6) + ",";
  json += "\"status\":\"Running\",";
  json += "\"speed_kmh\":0,";
  json += "\"eta_minutes\":0,";
  json += "\"passengers\":0";
  json += "}";

  int response = http.POST(json);

  Serial.print("Server Response: ");
  Serial.println(response);

  http.end();
}