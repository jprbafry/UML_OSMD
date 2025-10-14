#include <Thread.h>
#include <ThreadController.h>


// Thread controller manages all threads
ThreadController controller = ThreadController();

// --- Threads ---
Thread threadReceive = Thread();
Thread threadUpdate  = Thread();
Thread threadSend    = Thread();

// --- Shared variables ---
float des_light_azi = 0.0, des_light_pol = 0.0;
float des_detector_azi = 0.0, des_detector_pol = 0.0;

float cur_light_azi = 0.0, cur_light_pol = 0.0;
float cur_detector_azi = 0.0, cur_detector_pol = 0.0;

String inputBuffer = "";

// Step sizes
const float STEP_LIGHT    = 0.1;
const float STEP_DETECTOR = 0.2;

// Function declarations
void receiveTask();
void updateTask();
void sendTask();
void processInput(String msg);

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }  // Wait for Serial ready

  // --- Setup threads ---
  threadReceive.onRun(receiveTask);
  threadReceive.setInterval(5);   // check serial every 5 ms

  threadUpdate.onRun(updateTask);
  threadUpdate.setInterval(20);   // update currents every 10 ms

  threadSend.onRun(sendTask);
  threadSend.setInterval(40);     // send currents every 40 ms

  // Add to controller
  controller.add(&threadReceive);
  controller.add(&threadUpdate);
  controller.add(&threadSend);
}

void loop() {
  controller.run();  // this runs all active threads when ready
}

// --- Thread functions ---

// 1️⃣ Read from serial and parse desired values
void receiveTask() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (inputBuffer.length() > 0) {
        processInput(inputBuffer);
        inputBuffer = "";
      }
    } else {
      inputBuffer += c;
    }
  }
}

// 2️⃣ Update current values toward desired values
void updateTask() {
  auto moveTo = [](float &cur, float des, float step) {
    if (abs(cur - des) < step)
      cur = des;
    else if (cur < des)
      cur += step;
    else
      cur -= step;
  };

  moveTo(cur_light_azi, des_light_azi, STEP_LIGHT);
  moveTo(cur_light_pol, des_light_pol, STEP_LIGHT);
  moveTo(cur_detector_azi, des_detector_azi, STEP_DETECTOR);
  moveTo(cur_detector_pol, des_detector_pol, STEP_DETECTOR);
}

// 3️⃣ Send current values back to Raspberry Pi
void sendTask() {
  Serial.print(cur_light_azi, 1);
  Serial.print(',');
  Serial.print(cur_light_pol, 1);
  Serial.print(',');
  Serial.print(cur_detector_azi, 1);
  Serial.print(',');
  Serial.println(cur_detector_pol, 1);
}

// --- Helper to parse 4 comma-separated floats ---
void processInput(String msg) {
  float vals[4];
  int lastIndex = 0;
  int commaIndex = 0;

  for (int i = 0; i < 4; i++) {
    commaIndex = msg.indexOf(',', lastIndex);
    String token;

    if (commaIndex == -1 && i < 3) return;  // malformed
    if (commaIndex == -1)
      token = msg.substring(lastIndex);
    else
      token = msg.substring(lastIndex, commaIndex);

    vals[i] = token.toFloat();
    lastIndex = commaIndex + 1;
  }

  des_light_azi = vals[0];
  des_light_pol = vals[1];
  des_detector_azi = vals[2];
  des_detector_pol = vals[3];
}
