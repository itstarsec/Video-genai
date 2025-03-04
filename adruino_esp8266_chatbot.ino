#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <UniversalTelegramBot.h>

const char* ssid = "MIRAWAY";
const char* password = "Vuotso@2025";
const char* botToken = "6322621270:AAGapDbnqdVzPn68wQMdcKih3VtA_v1W3nk";
const char* chatId = "-4677628090";

WiFiClientSecure client;
UniversalTelegramBot bot(botToken, client);

const int RELAY_PIN = 0; // Chân GPIO điều khiển Relay
const char* serverUrl = "http://192.168.1.52:8888/detect";
String rtspUrl = "rtsp://192.168.1.52/1.mp4";


void handleNewMessages(int numNewMessages) {
    for (int i = 0; i < numNewMessages; i++) {
        String chat_id = bot.messages[i].chat_id;
        String text = bot.messages[i].text;
        
        if (text.startsWith("/rtsp ")) {
            rtspUrl = text.substring(6); // Lấy link stream từ lệnh
            bot.sendMessage(chat_id, "✅ Đã cập nhật luồng RTSP: " + rtspUrl, "");
        }
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH); // Tắt Relay khi khởi động

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    client.setInsecure();
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClient httpClient;
        HTTPClient http;
        http.begin(httpClient, serverUrl);
        http.addHeader("Content-Type", "application/json");
        
        // Tạo dữ liệu JSON
        StaticJsonDocument<200> jsonDoc;
        jsonDoc["rtsp_url"] = rtspUrl;
        String requestData;
        serializeJson(jsonDoc, requestData);
        
        int httpResponseCode = http.POST(requestData);
        if (httpResponseCode == HTTP_CODE_OK) {
            String response = http.getString();
            Serial.println("Response: " + response);
            
            StaticJsonDocument<200> responseDoc;
            deserializeJson(responseDoc, response);
            bool hasPerson = responseDoc["has_person"];
            
            if (hasPerson) {
                Serial.println("Người được phát hiện! Bật đèn trong 1 giây.");
                digitalWrite(RELAY_PIN, LOW);
                delay(1000);
                digitalWrite(RELAY_PIN, HIGH);
                Serial.println("Tắt đèn. Đợi tín hiệu tiếp theo...");
            }
        } else {
            Serial.printf("Lỗi kết nối API: %d\n", httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi mất kết nối. Đang thử kết nối lại...");
        WiFi.reconnect();
    }
    
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    if (numNewMessages > 0) {
        handleNewMessages(numNewMessages);
    }
    
    delay(5000); // Chờ 5 giây trước khi gửi request tiếp theo
}
