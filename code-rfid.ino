#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <UniversalTelegramBot.h>
#include <MFRC522.h>
#include <EEPROM.h>

const char* ssid = "MIRAWAY";
const char* password = "Vuotso@2025";
const char* botToken = "6322621270:AAGapDbnqdVzPn68wQMdcKih3VtA_v1W3nk";
const String chatID = "-4677628090"; // Chat ID dưới dạng String

#define RFID_RST_PIN 2
#define RFID_SS_PIN  15
#define RELAY_PIN 0 // Chân GPIO điều khiển Relay
#define EEPROM_SIZE 512

WiFiClientSecure client;
UniversalTelegramBot bot(botToken, client);
MFRC522 rfid_reader(RFID_SS_PIN, RFID_RST_PIN);

unsigned long relayOnTime = 0;
bool relayActive = false;

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
    
    client.setInsecure(); // Bỏ qua SSL
    SPI.begin();
    rfid_reader.PCD_Init(); // Khởi tạo RFID
    EEPROM.begin(EEPROM_SIZE); // Khởi tạo EEPROM
}

void loop() {
    check_for_new_card();

    // Điều khiển thời gian bật đèn
    if (relayActive && millis() - relayOnTime >= 1000) {
        digitalWrite(RELAY_PIN, LOW); // Tắt Relay (tắt đèn)
        Serial.println("Tắt đèn.");
        relayActive = false; // Đặt trạng thái relay
    }

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

            // Bật Relay (sáng đèn)
            digitalWrite(RELAY_PIN, HIGH); // Bật Relay (sáng đèn)
            Serial.println("Bật đèn.");
            relayOnTime = millis(); // Ghi lại thời gian bật đèn
            relayActive = true; // Đặt trạng thái relay là đang hoạt động

            process_card(rfid_reader.uid.uidByte, rfid_reader.uid.size); // Gọi hàm xử lý thẻ

            // Ngừng thẻ
            rfid_reader.PICC_HaltA();
            rfid_reader.PCD_StopCrypto1(); // Dừng mã hóa trên PCD
        }
    }
}

// Xử lý thẻ RFID
void process_card(byte* uid, byte uid_size) {
    if (!card_exists(uid, uid_size)) {
        save_card_uid(uid, uid_size);
        String uid_string = "Thẻ mới với UID: ";
        for (byte i = 0; i < uid_size; i++) {
            uid_string += (uid[i] < 0x10 ? " 0" : " ") + String(uid[i], HEX);
        }
        send_to_telegram(uid_string); // Gửi thông điệp UID đến Telegram
    } else {
        send_to_telegram("Thẻ đã được lưu trong hệ thống."); // Gửi thông điệp nếu thẻ đã tồn tại
    }
}

// Gửi thông điệp đến Telegram
void send_to_telegram(const String& message) {
    if (message != "") {
        bot.sendMessage(chatID, message, ""); // Gửi tin nhắn đến Telegram
    }
}

// Kiểm tra xem thẻ đã tồn tại trong EEPROM chưa
bool card_exists(byte* uid, byte uid_size) {
    for (int address = 0; address < EEPROM_SIZE; address += uid_size) {
        bool found = true;
        for (int i = 0; i < uid_size; i++) {
            if (EEPROM.read(address + i) != uid[i]) {
                found = false;
                break;
            }
        }
        if (found) return true;
    }
    return false;
}

// Lưu UID thẻ vào EEPROM
void save_card_uid(byte* uid, byte uid_size) {
    int address = find_empty_eeprom_address();
    if (address == -1) {
        Serial.println("Không có chỗ trống trong EEPROM để lưu UID");
        send_to_telegram("Không có chỗ trống trong EEPROM để lưu UID"); // Gửi thông điệp qua Telegram
        return;
    }
    for (int i = 0; i < uid_size; i++) {
        EEPROM.write(address + i, uid[i]);
    }
    EEPROM.commit(); // Ghi vào EEPROM
    send_to_telegram("UID của thẻ đã được lưu."); // Gửi thông điệp qua Telegram
}

// Tìm địa chỉ trống trong EEPROM
int find_empty_eeprom_address() {
    for (int address = 0; address < EEPROM_SIZE; address++) {
        if (EEPROM.read(address) == 255) {
            return address;
        }
    }
    return -1; // Không có chỗ trống
}
