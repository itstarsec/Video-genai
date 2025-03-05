#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define RELAY_PIN 0

const char* ssid = "MIRAWAY";
const char* password = "Vuotso@2025";
const char* url = "http://192.168.1.52:8888/status-check";

WiFiClient wifiClient;
HTTPClient http;

void setup() {
    Serial.begin(115200);
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW); // Tắt Relay khi khởi động

    // Kết nối Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    // In thông tin trạng thái WiFi
    printWiFiStatus();
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        http.begin(wifiClient, url);
        int httpCode = http.GET();
        
        if (httpCode > 0) {
            String payload = http.getString();
            Serial.println("Response: " + payload);
            
            DynamicJsonDocument doc(256);
            deserializeJson(doc, payload);
            
            String status = doc["status"];
            
            if (status == "yes") {
                digitalWrite(RELAY_PIN, HIGH);
                Serial.println("Relay ON");
            } else if (status == "no") {
                digitalWrite(RELAY_PIN, LOW);
                Serial.println("Relay OFF");
            }
        } else {
            Serial.println("Error on HTTP request");
        }
        
        http.end();
    }
    
    delay(5000); // Đợi 5 giây trước khi kiểm tra lại
}

void printWiFiStatus() {
    Serial.println("\nWiFi Status:");
    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Gateway IP: ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("DNS IP: ");
    Serial.println(WiFi.dnsIP());
    Serial.print("Subnet Mask: ");
    Serial.println(WiFi.subnetMask());
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
}
