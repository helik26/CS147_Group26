# CS147_Group26

Overview
This project demonstrates the use of an ESP32 microcontroller to read temperature and humidity data from an AHT20 sensor, display the readings on a TFT screen, and serve the data via an HTTP web server. The project utilizes the following components and libraries:

ESP32: The microcontroller for connecting to Wi-Fi and hosting the web server.
Adafruit AHT20: A temperature and humidity sensor.
TFT Display: For displaying real-time data.
Wi-Fi Connectivity: To serve sensor data via a web browser.

Hardware Requirements
ESP32 board
Adafruit AHT20 sensor
TFT display module (compatible with TFT_eSPI library)
Jumper wires for connections
Breadboard

How It Works
Sensor Initialization:
The AHT20 sensor is initialized over I²C.
The sensor reads temperature and humidity data.
TFT Display:
The temperature and humidity values are updated on the display every 2 seconds.
Web Server:
The ESP32 hosts a web server on port 80.
Sensor data is served as an HTML page with temperature and humidity readings.

Features
Real-Time Data Display:
Temperature and humidity readings are displayed on the TFT screen.
Web Interface:
Access sensor data via a web browser.
Simple HTTP Server:
Serves data as a user-friendly HTML page.
