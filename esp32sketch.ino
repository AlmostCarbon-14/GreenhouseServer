#include <WiFi.h>
#include "DHT.h"
#include <WiFiUdp.h>

#define TEMPPIN 16
#define PUMP1 12
#define PUMP2 13

const char* ssids[] = {"FiOS-OUWC1", "Downstairs Wi-Fi", "Master Bedroom Wi-fi"};
const char* password = "tip0579fans20wakes";
IPAddress my_ip(192, 168, 1, 247);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 0, 0);
DHT dht(TEMPPIN, DHT11);
const int sendPort = 6556;
const int recvPort = 6557;
const char * serverADDR = "192.168.1.112";
char recvBuffer[255];
char respBuffer[16];

WiFiUDP sendPacket, recvPacket;
TaskHandle_t DHTPACK;
TaskHandle_t INSTRRECV;

void setup() {
  WiFi.disconnect(true);
  delay(1000);
  Serial.begin(115200);
  Serial.print("setup() running on core ");
  Serial.println(xPortGetCoreID());
  WiFi.mode(WIFI_STA);
  WiFi.config(my_ip, gateway, subnet);
  WiFi.setHostname("Greenhouse-Pump");
  connectToWifi();
  WiFi.onEvent(WiFiDisconnect, SYSTEM_EVENT_STA_DISCONNECTED);
  sendPacket.begin(sendPort);
  recvPacket.begin(recvPort);
  dht.begin();
  pinMode(PUMP1, OUTPUT);
  pinMode(PUMP2, OUTPUT);
  xTaskCreatePinnedToCore(sendTempHumidPacket, "DHT11 Packet", 10000, NULL, 1, &DHTPACK, 0);
  delay(1000);
  xTaskCreatePinnedToCore(recvInstructionFromServer, "Instr Recv", 10000, NULL, 1, &INSTRRECV, 1);
  delay(1000);
}

void sendTempHumidPacket(void * pvParameters) {
  for(;;) {
    float humi = dht.readHumidity();
    float temp = dht.readTemperature();
    sendPacket.beginPacket(serverADDR, sendPort);
    sprintf(respBuffer, "%f,%f", humi, cToF(temp));
    sendPacket.printf(respBuffer);
    sendPacket.endPacket();
    delay(10000);
  }
}

void recvInstructionFromServer(void * pvParameters) {
  for(;;) {
    memset(recvBuffer, 0, 255);
    recvPacket.parsePacket();
    if(recvPacket.read(recvBuffer, 50) > 0) {
      char * instruction = strtok(recvBuffer, ",");
      if (instruction != 0) {
        int runTime = atoi(strtok(NULL, ","));
        int instr = atoi(instruction);
        switch(instr) {
            case 555:
              Serial.println("Running Pump1");
              Serial.print("Delay is ");
              Serial.print(runTime);
              Serial.println(" seconds long");
              digitalWrite(PUMP1, HIGH);
              delay(runTime * 1000);
              digitalWrite(PUMP1, LOW);
              break;
            case 560:
              Serial.println("Running Pump2");
              Serial.print("Delay is ");
              Serial.print(runTime);
              Serial.println(" seconds long");
              digitalWrite(PUMP2, HIGH);
              delay(runTime * 1000);
              digitalWrite(PUMP2, LOW);
              break;
            case 565:
              Serial.println("Rebooting");break;
          }
      }
    }
    delay(1000);
  }
}

void loop() {
}

void connectToWifi() {
  int attempts = 0;
  for (int i = 0; i < 3; i++) {
      Serial.print("Attempting to connect to AP: ");
      Serial.println(ssids[i]);
      WiFi.begin(ssids[i], password);
      while (attempts < 10 && WiFi.status() != WL_CONNECTED) {
        Serial.print("Attempt: ");
        Serial.println(attempts);
        delay(1000);
        attempts++;
      }
      if (attempts < 10) {
        Serial.print("Connected to ");
        Serial.print(ssids[i]);
        Serial.println(" Successfully!");
        break;
      }
      attempts = 0;
  }
  if (attempts == 10) {
    ESP.restart();
  }
}

void WiFiDisconnect(WiFiEvent_t event, WiFiEventInfo_t info) {
  Serial.println("Disconnected from WiFi access point");
  Serial.print("WiFi lost connection. Reason: ");
  Serial.println(info.disconnected.reason);
  Serial.println("Trying to Reconnect");
  connectToWifi();
}

float cToF(float temp) {
  return temp * (9/5) + 32; 
}
