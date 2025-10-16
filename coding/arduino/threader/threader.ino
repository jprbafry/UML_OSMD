#include <Wire.h>
#include <MPU6050.h>

#include <Thread.h>
#include <ThreadController.h>

#define BAUD_RATE 250000 //115200

// -------------------------
// Sensor Data Structure
// -------------------------
struct SensorData {
  // Angular Position
  int pot_light;     // Potentiometer Light Source
  int pot_detector;     // Potentiometer Detector
  // Light Intensity
  int ref_diode;     // Reference Diode
  // Homing/EndStop
  bool home_light_rad;   // Homing/EndStop Switch #1 (Light Radial/Polar)
  bool home_detector_rad;   // Homing/EndStop Switch #2 (Detector Radial/Polar)
  bool home_light_azi;   // Homing/EndStop Switch #3 (Light Azimuthal)
  bool home_detector_azi;   // Homing/EndStop Switch #4 (Detector Azimuthal)
  // IMU data
  float accelX, accelY, accelZ;
  float gyroX, gyroY, gyroZ;
};

// Global instance
SensorData sensors;

// -------------------------
// Thread Controller
// -------------------------
ThreadController controller;

// Sensor Threads
Thread potAziThread;
Thread refdiodeThread;
Thread homeRadThread;
Thread homeAziThread;

// Serial Thread
Thread printThread;

// IMU Thread
Thread imuThread;

// 
Thread ledThread;

// -------------------------
// Pin Definitions
// -------------------------

/* ADC Pins */
const int PIN_POT_LIGHT = A0;
const int PIN_POT_DETECTOR = A1;
const int PIN_REFDIODE = A2;

/* GPIO Pins (Pull-Up) */
const int PIN_HOME_SWT_LIGHT_RAD = 47;
const int PIN_HOME_SWT_LIGHT_AZI = 49;
const int PIN_HOME_SWT_DETECTOR_RAD = 48;
const int PIN_HOME_SWT_DETECTOR_AZI = 50;

const int PIN_LED_1 = 27;
const int PIN_LED_2 = 28;


MPU6050 imu;
void readIMU() {
  sensors.accelX = imu.getAccelerationX();
  sensors.accelY = imu.getAccelerationY();
  sensors.accelZ = imu.getAccelerationZ();
  sensors.gyroX  = imu.getRotationX();
  sensors.gyroY  = imu.getRotationY();
  sensors.gyroZ  = imu.getRotationZ();
}


// -------------------------
// Thread 'Periods'
// -------------------------

const int PER_POT_AZI = 100;
const int PER_REFDIODE = 100;
const int PER_HOME_POLAR = 100;
const int PER_HOME_AZIMUTHAL = 100;
const int PER_LED = 50;
const int PER_LED2 = 50;
const int PER_PRINTER = 1000;
const int PER_IMU = 100; 

// -------------------------
// Thread Functions
// -------------------------
void readPotentiometers() {
  sensors.pot_light = analogRead(PIN_POT_LIGHT);
  sensors.pot_detector = analogRead(PIN_POT_DETECTOR);
}

void readRefDiode() {
  sensors.ref_diode = analogRead(PIN_REFDIODE);
}

void readPolarHomingSwitches() {
  sensors.home_light_rad = !digitalRead(PIN_HOME_SWT_LIGHT_RAD); // Active low
  sensors.home_detector_rad = !digitalRead(PIN_HOME_SWT_DETECTOR_RAD);
}

void readAzimuthalHomingSwitches() {
  sensors.home_light_azi = !digitalRead(PIN_HOME_SWT_LIGHT_AZI);
  sensors.home_detector_azi = !digitalRead(PIN_HOME_SWT_DETECTOR_AZI);
}

void ledControl() {
  digitalWrite(PIN_LED_1, sensors.home_detector_rad ? HIGH : LOW);
  digitalWrite(PIN_LED_2, sensors.home_light_rad ? HIGH : LOW);
}

void printSensors() {

  Serial.print("Signals ... ");
  Serial.print(" Light_pot: "); Serial.print(sensors.pot_light);
  Serial.print(" Detector_pot: "); Serial.print(sensors.pot_detector);
  Serial.print(" Ref_diode: "); Serial.print(sensors.ref_diode);
  Serial.print("\n");

  Serial.print("Homing ... ");  
  Serial.print(" Light_rad: "); Serial.print(sensors.home_light_rad);
  Serial.print(" Light_azi: "); Serial.print(sensors.home_light_azi);
  Serial.print(" Detector_rad: "); Serial.print(sensors.home_detector_rad);
  Serial.print(" Detector_azi: "); Serial.print(sensors.home_detector_azi);
  Serial.print("\n");

  Serial.print("IMU ... ");
  Serial.print(" Ax: "); Serial.print(sensors.accelX);
  Serial.print(" Ay: "); Serial.print(sensors.accelY);
  Serial.print(" Az: "); Serial.print(sensors.accelZ);
  Serial.print(" Gx: "); Serial.print(sensors.gyroX);
  Serial.print(" Gy: "); Serial.print(sensors.gyroY);
  Serial.print(" Gz: "); Serial.println(sensors.gyroZ);

}

// -------------------------
// Setup
// -------------------------
void setup() {
  Serial.begin(BAUD_RATE);
  
  
  
  Wire.begin();
  imu.initialize();

  if (!imu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
  } else {
    Serial.println("MPU6050 connected successfully.");
  }


  // ADC pins are automatically inputs
  pinMode(PIN_HOME_SWT_LIGHT_RAD, INPUT_PULLUP);
  pinMode(PIN_HOME_SWT_LIGHT_AZI, INPUT_PULLUP);
  pinMode(PIN_HOME_SWT_DETECTOR_RAD, INPUT_PULLUP);
  pinMode(PIN_HOME_SWT_DETECTOR_AZI, INPUT_PULLUP);

  pinMode(PIN_LED_1, OUTPUT);
  pinMode(PIN_LED_2, OUTPUT);

  // -------------------------
  // Configure Threads
  // -------------------------
  potAziThread.onRun(readPotentiometers);
  potAziThread.setInterval(PER_POT_AZI);

  refdiodeThread.onRun(readRefDiode);
  refdiodeThread.setInterval(PER_REFDIODE);

  homeRadThread.onRun(readPolarHomingSwitches);
  homeRadThread.setInterval(PER_HOME_POLAR);

  homeAziThread.onRun(readAzimuthalHomingSwitches);
  homeAziThread.setInterval(PER_HOME_AZIMUTHAL);

  ledThread.onRun(ledControl);
  ledThread.setInterval(PER_LED);

  printThread.onRun(printSensors);
  printThread.setInterval(PER_PRINTER);

  imuThread.onRun(readIMU);
  imuThread.setInterval(PER_IMU);

  // Add threads to controller
  controller.add(&potAziThread);
  controller.add(&refdiodeThread);
  controller.add(&homeRadThread);
  controller.add(&homeAziThread);
  controller.add(&ledThread);
  controller.add(&printThread);
  controller.add(&imuThread);

}

// -------------------------
// Main Loop
// -------------------------
void loop() {
  controller.run();
}
