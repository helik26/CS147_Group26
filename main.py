//source Code
#include <WiFi.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <Adafruit_SSD1306.h>

#define DHTPIN 15 // Pin connected to the DHT sensor
#define DHTTYPE DHT11
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

DHT dht(DHTPIN, DHTTYPE);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

const char* ssid = "your-SSID";
const char* password = "your-PASSWORD";

void setup() {
  Serial.begin(115200);
  dht.begin();

  if (!display.begin(SSD1306_I2C_ADDRESS, 0x3C)) {
    Serial.println("SSD1306 allocation failed");
    for (;;);
  }
  display.display();
  delay(2000);
  display.clearDisplay();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
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

