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

  // Handle Web Server Client
  WiFiClient client = server.available();  // Listen for incoming clients
  if (client) {
    Serial.println("New Client Connected");
    String currentLine = "";  // To hold incoming data
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);  // Print received data to Serial Monitor

        // If the client sends a newline, process the request
        if (c == '\n') {
          // Send HTTP response
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");
          client.println();

          // HTML content
          client.println("<!DOCTYPE html>");
          client.println("<html>");
          client.println("<head><title>ESP32 Sensor Data</title></head>");
          client.println("<body>");
          client.println("<h1>Temperature and Humidity</h1>");
          client.print("<p>Temperature: ");
          client.print(temp.temperature, 2);  // 2 decimal places
          client.println(" &deg;C</p>");
          client.print("<p>Humidity: ");
          client.print(humidity.relative_humidity, 2);  // 2 decimal places
          client.println(" %</p>");
          client.println("</body>");
          client.println("</html>");
          break;  // Stop processing the client
        }
      }
    }
    // Close the connection
    client.stop();
    Serial.println("Client Disconnected");
  }

  // Wait before updating again
  delay(2000);  // Update every 2 seconds
}

