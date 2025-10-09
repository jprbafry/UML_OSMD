#include <Arduino.h>
#include <Thread.h>
#include <ThreadController.h>

/* 

This code creates three cooperative (as oppposed to preemptive) threads
    - tempThread: produces temperature data
    - accelThread: produces accelerometer data
    - printThread: prints data on serial port
*/


// --------------------------------------
// Data structure
// --------------------------------------
struct SensorData {
  float temperature;
  float accelX;
  float accelY;
  float accelZ;
};

SensorData sensors;

// --------------------------------------
// Threads
// --------------------------------------
ThreadController controller;
Thread tempThread;
Thread accelThread;
Thread printThread;

// --------------------------------------
// Timing
// --------------------------------------
unsigned long startMillis;

// --------------------------------------
// Helper: pseudo-random float in [-range, +range]
// --------------------------------------
float randNoise(float range) {
  return ((float)random(-1000, 1000) / 1000.0f) * range;
}

// --------------------------------------
// Thread functions
// --------------------------------------

// Temperature: sinusoidal over 1 day (24h), amplitude 8°C, offset 16°C, ±0.1 noise
void updateTemperature() {
  float t_sec = (millis() - startMillis) / 1000.0f;
  const float day_period = 24.0f * 60.0f * 60.0f; // seconds in one day
  const float omega = 2.0f * PI / day_period;     // angular frequency
  float temp = 16.0f + 8.0f * sin(omega * t_sec); // offset + amplitude*sin()
  temp += randNoise(0.1f);
  sensors.temperature = temp;
}

// Accelerometer: 3 sine waves with different frequencies & phases
void updateAccel() {
  float t = (millis() - startMillis) / 1000.0f;
  // 0.5 g amplitude maximum
  sensors.accelX = 0.5f * sin(2 * PI * t / 2.0f);       // period = 2 s
  sensors.accelY = 0.5f * sin(2 * PI * t / 3.0f + PI/4); // period = 3 s
  sensors.accelZ = 0.5f * sin(2 * PI * t / 5.0f + PI/2); // period = 5 s
}

// Print thread
void printSensors() {
  //Serial.print("Temp: ");
  //Serial.print(sensors.temperature, 2);
  Serial.print("°C  Accel[g]: ");
  Serial.print(sensors.accelX, 3); Serial.print(", ");
  Serial.print(sensors.accelY, 3); Serial.print(", ");
  Serial.println(sensors.accelZ, 3);
}

// --------------------------------------
// Setup
// --------------------------------------
void setup() {
  Serial.begin(115200);
  delay(500);
  randomSeed(analogRead(A0)); // seed noise
  startMillis = millis();

  // Configure threads
  tempThread.onRun(updateTemperature);
  tempThread.setInterval(1000);   // every 1 second

  accelThread.onRun(updateAccel);
  accelThread.setInterval(50);    // every 50 ms (20 Hz)

  printThread.onRun(printSensors);
  printThread.setInterval(500);   // every 0.5 second

  // Add to controller
  controller.add(&tempThread);
  controller.add(&accelThread);
  controller.add(&printThread);
}

// --------------------------------------
// Loop
// --------------------------------------
void loop() {
  controller.run();
}
