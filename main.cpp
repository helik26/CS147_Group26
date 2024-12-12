#include <TFT_eSPI.h>
#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <WiFi.h>
#include <HttpClient.h>
#include <nvs.h>
#include <nvs_flash.h>

// TFT Display Object
TFT_eSPI tft = TFT_eSPI();

// I²C Configuration
#define SDA_PIN 21  // SDA connected to GPIO 21
#define SCL_PIN 22  // SCL connected to GPIO 22

// Adafruit AHT20 Sensor Object
Adafruit_AHTX0 aht;

// Wi-Fi credentials
char ssid[50];  // Wi-Fi SSID
char pass[50];  // Wi-Fi Password

// Server Information
const char kHostname[] = "18.227.140.251";  // Replace with your server IP
const int kPort = 5000;  // Replace with your server's port

// Timing Configuration
const int kNetworkTimeout = 30 * 1000;  // 30 seconds
const int kNetworkDelay = 1000;  // 1 second

void nvs_access() {
  // Initialize NVS
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    err = nvs_flash_init();
  }
  ESP_ERROR_CHECK(err);

  // Open NVS
  Serial.printf("\nOpening Non-Volatile Storage (NVS) handle... ");
  nvs_handle_t my_handle;
  err = nvs_open("storage", NVS_READWRITE, &my_handle);
  if (err != ESP_OK) {
    Serial.printf("Error (%s) opening NVS handle!\n", esp_err_to_name(err));
  } else {
    Serial.printf("Done\n");
    Serial.printf("Retrieving SSID/PASSWD\n");

    size_t ssid_len = sizeof(ssid);
    size_t pass_len = sizeof(pass);
    err = nvs_get_str(my_handle, "ssid", ssid, &ssid_len);
    err |= nvs_get_str(my_handle, "pass", pass, &pass_len);

    if (err == ESP_ERR_NVS_NOT_FOUND) {
      Serial.printf("SSID and password not found in NVS. Saving new credentials.\n");

      // Replace with your Wi-Fi credentials
      strcpy(ssid, "Your_SSID");
      strcpy(pass, "Your_Password");

      // Save credentials to NVS
      nvs_set_str(my_handle, "ssid", ssid);
      nvs_set_str(my_handle, "pass", pass);
      nvs_commit(my_handle);
    } else if (err != ESP_OK) {
      Serial.printf("Error (%s) reading from NVS!\n", esp_err_to_name(err));
    } else {
      Serial.printf("Done. SSID: %s, PASS: %s\n", ssid, pass);
    }
  }

  // Close NVS
  nvs_close(my_handle);
}

void setup() {
  // Initialize Serial for debugging
  Serial.begin(9600);
  delay(1000);

  // Initialize the TFT display
  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(2);

  // Initialize I²C
  Wire.begin(SDA_PIN, SCL_PIN);

  // Initialize the sensor
  if (!aht.begin()) {
    Serial.println("Could not find AHT20 sensor! Check wiring.");
    while (1) delay(10);
  }
  Serial.println("AHT20 sensor initialized.");

  // Retrieve Wi-Fi credentials
  nvs_access();

  // Connect to Wi-Fi
  Serial.println();
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected");
  Serial.println("IP Address: " + WiFi.localIP().toString());
}

void loop() {
  // Read temperature and humidity
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);

  // Log Sensor Data
  Serial.print("Temperature: ");
  Serial.print(temp.temperature);
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(humidity.relative_humidity);
  Serial.println(" %");

  // Display Data on TFT Screen
  tft.fillScreen(TFT_BLACK);  // Clear the screen
  tft.setCursor(0, 0);
  tft.print("Temperature: ");
  tft.println(temp.temperature, 2);  // Display temperature with 2 decimals
  tft.print("Humidity: ");
  tft.println(humidity.relative_humidity, 2);  // Display humidity with 2 decimals

  // Construct the dynamic kPath with updated temperature and humidity values
  String kPath = String("/?temp=") + String(temp.temperature, 2) + "&humidity=" + String(humidity.relative_humidity, 2);

  // Send Data to the Server
  WiFiClient c;
  HttpClient http(c);

  // Make HTTP GET Request
  int err = http.get(kHostname, kPort, kPath.c_str());
  if (err == 0) {
    Serial.println("Request sent successfully");

    // Read Response
    int statusCode = http.responseStatusCode();
    if (statusCode >= 0) {
      Serial.print("Response Status Code: ");
      Serial.println(statusCode);

      int contentLength = http.contentLength();
      Serial.print("Content Length: ");
      Serial.println(contentLength);

      Serial.println("Response Body:");
      while (http.connected() || http.available()) {
        if (http.available()) {
          char c = http.read();
          Serial.print(c);
        }
      }
    } else {
      Serial.print("Error getting response: ");
      Serial.println(statusCode);
    }
  } else {
    Serial.print("Connection failed: ");
    Serial.println(err);
  }
  http.stop();

  // Wait before sending the next request
  delay(5000);
}

