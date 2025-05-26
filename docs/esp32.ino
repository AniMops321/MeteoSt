#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>

#define BME280_ADDRESS 0x76

const char* ssid = "ВАША_СЕТЬ";
const char* password = "ПАРОЛЬ";
const char* serverURL = "http://192.168.1.100:5000/data";  // IP вашего компьютера с Flask

Adafruit_BME280 bme;
BH1750 lightMeter;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  WiFi.begin(ssid, password);
  Serial.print("Подключение к Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Подключено к Wi-Fi");

  if (!bme.begin(BME280_ADDRESS)) {
    Serial.println("❌ BME280/BMP280 не найден!");
    while (1);
  }

  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("❌ BH1750 не найден!");
    while (1);
  }
}

void loop() {
  float temp = bme.readTemperature();
  float pressure = bme.readPressure() / 100.0F;
  float humidity = bme.readHumidity();
  float lux = lightMeter.readLightLevel();

  // Вывод в монитор порта
  Serial.println("---- Данные ----");
  Serial.printf("Темп: %.2f °C\n", temp);
  Serial.printf("Давление: %.2f hPa\n", pressure);
  if (!isnan(humidity)) Serial.printf("Влажность: %.2f %%\n", humidity);
  else Serial.println("Влажность: ❌");
  Serial.printf("Освещённость: %.2f лк\n", lux);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"temperature\":" + String(temp, 2) + ",";
    json += "\"pressure\":" + String(pressure, 2) + ",";
    json += "\"humidity\":" + String(humidity, 2) + ",";
    json += "\"lux\":" + String(lux, 2);
    json += "}";

    int httpResponseCode = http.POST(json);
    Serial.printf("Ответ сервера: %d\n", httpResponseCode);
    http.end();
  }

  delay(10000);  // каждые 10 секунд
}
