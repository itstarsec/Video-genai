#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <MFRC522.h>
#include <EEPROM.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "MIRAWAY";
const char* password = "Vuotso@2025";
const char* checkStatusUrl = "http://192.168.1.52:8888/status-check"; // Endpoint kiểm tra trạng thái
const char* updateStatusUrl = "http://192.168.1.52:8888/update-status"; // Endpoint cập nhật trạng thái

#define RFID_RST_PIN 2
#define RFID_SS_PIN  15
#define RELAY_PIN 0 // Chân GPIO điều khiển Relay
#define EEPROM_SIZE 512

WiFiClient wifiClient;
MFRC522 rfid_reader(RFID_SS_PIN, RFID_RST_PIN);

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

    SPI.begin();
    rfid_reader.PCD_Init(); // Khởi tạo RFID
    EEPROM.begin(EEPROM_SIZE); // Khởi tạo EEPROM
}

void loop() {
    check_for_new_card(); // Kiểm tra thẻ RFID mới

    // Kiểm tra trạng thái từ server để điều khiển relay
    check_status_from_server();

    delay(100); // Thời gian nghỉ ngắn để tránh sử dụng CPU quá tải
}

// Kiểm tra thẻ RFID mới
void check_for_new_card() {
    if (rfid_reader.PICC_IsNewCardPresent()) {
        if (rfid_reader.PICC_ReadCardSerial()) {
            Serial.print("UID: ");
            for (int i = 0; i < rfid_reader.uid.size; i++) {
                Serial.print(rfid_reader.uid.uidByte[i] < 0x10 ? " 0" : " ");
                Serial.print(rfid_reader.uid.uidByte[i], HEX);
            }
            Serial.println();

            // Gọi hàm xử lý thẻ
            process_card(rfid_reader.uid.uidByte, rfid_reader.uid.size); 

            // Ngừng thẻ
            rfid_reader.PICC_HaltA();
            rfid_reader.PCD_StopCrypto1(); // Dừng mã hóa trên PCD
        }
    }
}

// Xử lý thẻ RFID
void process_card(byte* uid, byte uid_size) {
    // Kiểm tra điều kiện UID 
    if (uid_size == 4) { // Đảm bảo UID có độ dài tương ứng
        if (uid[0] == 0x99 && uid[1] == 0x4F && uid[2] == 0xCD && uid[3] == 0x01) {
            send_status_to_server("yes");
        } else if (uid[0] == 0xCE && uid[1] == 0x3B && uid[2] == 0xB4 && uid[3] == 0x02) {
            send_status_to_server("no");
        } else {
            Serial.println("Thẻ RFID không hợp lệ.");
        }
    }
}

// Gửi trạng thái đến server
void send_status_to_server(const String& status) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(wifiClient, updateStatusUrl);
        
        // Tạo JSON payload
        String jsonPayload = "{\"status\": \"" + status + "\"}";

        http.addHeader("Content-Type", "application/json");
        int httpCode = http.POST(jsonPayload);
        
        if (httpCode > 0) {
            String response = http.getString();
            Serial.println("Response: " + response);
        } else {
            Serial.println("Error on HTTP request");
        }
        
        http.end();
    } else {
        Serial.println("WiFi is not connected.");
    }
}

// Kiểm tra trạng thái từ server để điều khiển relay
void check_status_from_server() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(wifiClient, checkStatusUrl);
        
        int httpCode = http.GET();
        
        if (httpCode > 0) {
            String payload = http.getString();
            Serial.println("Response: " + payload);
            
            DynamicJsonDocument doc(256);
            deserializeJson(doc, payload);
            
            String status = doc["status"];
            
            if (status == "yes") {
                digitalWrite(RELAY_PIN, HIGH); // Bật relay
                Serial.println("Relay ON");
            } else if (status == "no") {
                digitalWrite(RELAY_PIN, LOW); // Tắt relay
                Serial.println("Relay OFF");
            }
        } else {
            Serial.println("Error on HTTP request");
        }
        
        http.end();
    } else {
        Serial.println("WiFi is not connected.");
    }
}
