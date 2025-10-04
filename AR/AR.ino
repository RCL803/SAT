#include <WiFi.h>
#include <WebServer.h>

// ===== WiFi 設定 =====
const char* ssid = "LASER";
const char* password = "12345678";

// ===== LED 腳位 =====
#define LED_GREEN 2

// ===== WebServer =====
WebServer server(80);

// ===== LED 控制 =====
void handleGreenOn()  { 
  digitalWrite(LED_GREEN,HIGH);  
  server.send(200,"text/plain","GREEN ON"); 
}

void handleGreenOff() { 
  digitalWrite(LED_GREEN,LOW);   
  server.send(200,"text/plain","GREEN OFF"); 
}

// ===== 網頁首頁 =====
void handleRoot() {
  String html = "<html><body>";
  html += "<h1>ESP32 LED Control</h1>";

  // 注意：將 <筆電IP> 改成你的筆電局域網 IP，例如 192.168.1.100
  html += "<img src=\"http://172.20.10.4:5000/video_feed\" width=\"320\"><br><br>";

  html += "<button onclick=\"fetch('/green/on').then(r=>r.text().then(alert))\">LED ON</button>";
  html += "<button onclick=\"fetch('/green/off').then(r=>r.text().then(alert))\">LED OFF</button><br>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

// ===== 404 =====
void handleNotFound() { 
  server.send(404,"text/plain","Not found"); 
}

// ===== setup =====
void setup() {
  Serial.begin(115200);
  pinMode(LED_GREEN, OUTPUT);
  digitalWrite(LED_GREEN, LOW);

  // 連線 WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while(WiFi.status() != WL_CONNECTED){ 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println();
  Serial.print("WiFi connected. IP: "); 
  Serial.println(WiFi.localIP());

  // 設定 HTTP 路由
  server.on("/", HTTP_GET, handleRoot);
  server.on("/green/on",  handleGreenOn);
  server.on("/green/off", handleGreenOff);
  server.onNotFound(handleNotFound);

  server.begin();
  Serial.println("HTTP Server 已啟動");
}

// ===== loop =====
void loop() {
  server.handleClient();  // 處理 HTTP 請求
}
