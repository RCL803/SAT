#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// ===== WiFi 設定 =====
const char* ssid = "LASER";
const char* password = "12345678";

// ===== LED 腳位 =====
#define LED_GREEN 14
#define LED_YELLOW 32
#define LED_RED 33

// ===== ESP32-CAM 腳位 =====
#define Y2_GPIO_NUM 4
#define Y3_GPIO_NUM 5
#define Y4_GPIO_NUM 18
#define Y5_GPIO_NUM 19
#define Y6_GPIO_NUM 36
#define Y7_GPIO_NUM 39
#define Y8_GPIO_NUM 34
#define Y9_GPIO_NUM 35
#define XCLK_GPIO_NUM 21
#define PCLK_GPIO_NUM 22
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define PWDN_GPIO_NUM -1
#define RESET_GPIO_NUM -1

WebServer server(80);

// ===== 相機初始化 =====
void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("相機初始化失敗");
    return;
  }
  Serial.println("相機初始化成功");
}

// ===== 串流處理 =====
void handleStream() {
  WiFiClient client = server.client();
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println();

  camera_fb_t *fb;
  while (client.connected()) {
    fb = esp_camera_fb_get();
    if (!fb) break;
    client.println("--frame");
    client.println("Content-Type: image/jpeg");
    client.println("Content-Length: " + String(fb->len));
    client.println();
    client.write(fb->buf, fb->len);
    client.println();
    esp_camera_fb_return(fb);
  }
}

// ===== LED 控制 =====
void handleLed(String color, bool state) {
  int pin;
  if (color == "green") pin = LED_GREEN;
  else if (color == "yellow") pin = LED_YELLOW;
  else if (color == "red") pin = LED_RED;
  else {
    server.send(404, "text/plain", "LED not found");
    return;
  }
  digitalWrite(pin, state ? HIGH : LOW);
  server.send(200, "text/plain", (state ? "ON" : "OFF"));
}

// ===== setup =====
void setup() {
  Serial.begin(115200);

  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);

  WiFi.begin(ssid, password);
  Serial.print("WiFi 連線中");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\n✅ WiFi 已連線");
  Serial.print("IP: "); Serial.println(WiFi.localIP());

  startCamera();

  // 註冊路由
  server.on("/stream", handleStream);
  server.on("/on/green", []() { handleLed("green", true); });
  server.on("/off/green", []() { handleLed("green", false); });
  server.on("/on/yellow", []() { handleLed("yellow", true); });
  server.on("/off/yellow", []() { handleLed("yellow", false); });
  server.on("/on/red", []() { handleLed("red", true); });
  server.on("/off/red", []() { handleLed("red", false); });

  server.begin();
  Serial.println("HTTP Server 已啟動");
}

void loop() {
  server.handleClient();
}
