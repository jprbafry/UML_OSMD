#include <Thread.h>
#include <ThreadController.h>


 
// === Pin Definitions ===
// Make sure pins match your setup
#define DET_AZ_STEP 34
#define DET_AZ_DIR 35
#define DET_RAD_STEP 32
#define DET_RAD_DIR 33
#define LIGHT_AZ_STEP 36
#define LIGHT_AZ_DIR 37
#define LIGHT_RAD_STEP 30
#define LIGHT_RAD_DIR 31


// === Constants ===
// TODO: Change if necessary (how many steps the motor does per degree depends on the setup)
const float DET_AZ_STEPS_PER_DEG = 12.0;
const float DET_RAD_STEPS_PER_DEG = 10.0;
const float LIGHT_AZ_STEPS_PER_DEG = 12.0;
const float LIGHT_RAD_STEPS_PER_DEG = 10.0;


const unsigned int NUM_MOTORS = 4; // How many motors do we have
const unsigned int STEP_DELAY_US = 500;  // Motor speed control



// === Enum for Axis Selection ===
enum MotorAxis {
    DETECTOR_AZ,
    DETECTOR_RAD,
    LIGHT_AZ,
    LIGHT_RAD
};



// === Motor struct ===
struct Motor {
    const char *name;
    int step_pin;
    int dir_pin;
    float steps_per_deg;
    long current_steps;     // stored "actual" steps (updated from encoder)
};


Motor motors[NUM_MOTORS];









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

// === Function Prototypes ===
void receiveTask();
void updateTask();
void sendTask();
void processInput(String msg);
void move_to_absolute(MotorAxis axis, float target_angle);
void reset_position();
Motor* get_motor(MotorAxis axis);

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }  // Wait for Serial ready





  // initialize motor table (match pins and initial 8 degrees)
  motors[DETECTOR_AZ]  = {"DET_AZ",  DET_AZ_STEP,  DET_AZ_DIR};
  motors[DETECTOR_RAD] = {"DET_RAD", DET_RAD_STEP, DET_RAD_DIR};
  motors[LIGHT_AZ]     = {"LIGHT_AZ",LIGHT_AZ_STEP, LIGHT_AZ_DIR};
  motors[LIGHT_RAD]    = {"LIGHT_RAD",LIGHT_RAD_STEP, LIGHT_RAD_DIR};

  // Setup pins and encoders
  for (int i = 0; i < NUM_MOTORS; ++i) {
    pinMode(motors[i].step_pin, OUTPUT);
    pinMode(motors[i].dir_pin, OUTPUT);
  }

  Serial.println("Motor controller ready.");

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


// === Auxiliary functions ===


Motor* get_motor(MotorAxis axis) {
    return &motors[(int)axis];
}

void move_to_absolute(MotorAxis axis, float target_angle) {

    Motor* m = get_motor(axis);
  
    long target_steps = lround(target_angle * m->steps_per_deg);
    long step_diff = target_steps - m->current_steps;
    bool direction = (step_diff >= 0);
    long move_steps = abs(step_diff);
    
    digitalWrite(m->dir_pin, direction ? HIGH : LOW);
    for (long i = 0; i < move_steps; i++) {
      digitalWrite(m->step_pin, HIGH);
      delayMicroseconds(STEP_DELAY_US);
      digitalWrite(m->step_pin, LOW);
      delayMicroseconds(STEP_DELAY_US);
    }
  
    long starting_pos = m->current_steps;
    m->current_steps = target_steps;
  
    // Serial.print("Moved ");
    // Serial.print(m->name);
    // Serial.print(" from ");
    // Serial.print(lround((float)starting_pos / m->steps_per_deg));
    // Serial.print(" to ");
    // Serial.print(target_angle, 2);
    // Serial.print(" degrees. (");
    // Serial.print(move_steps);
    // Serial.println(" steps)");
    // Serial.println("OK");
}

// Update current values toward desired values
void moveTo(float &cur, float des, float step) {
    if (abs(cur - des) < step)
      cur = des;
    else if (cur < des)
      cur += step;
    else
      cur -= step;
};



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



// --- Thread functions ---

// Read from serial and parse desired values
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



void updateTask() {
  moveTo(cur_light_azi, des_light_azi, STEP_LIGHT);
  moveTo(cur_light_pol, des_light_pol, STEP_LIGHT);
  moveTo(cur_detector_azi, des_detector_azi, STEP_DETECTOR);
  moveTo(cur_detector_pol, des_detector_pol, STEP_DETECTOR);
}

// Send current values back to Raspberry Pi
void sendTask() {
  Serial.print(cur_light_azi, 1);
  Serial.print(',');
  Serial.print(cur_light_pol, 1);
  Serial.print(',');
  Serial.print(cur_detector_azi, 1);
  Serial.print(',');
  Serial.println(cur_detector_pol, 1);
}
