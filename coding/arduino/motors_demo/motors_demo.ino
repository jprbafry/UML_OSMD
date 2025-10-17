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
const unsigned int STEP_DELAY_US = 500;  



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


#define MOTION_PERIOD 20
#define RECEPTION_PERIOD 5
#define TRANSMISSION_PERIOD 40

// --- Threads ---
Thread threadReceive = Thread();
Thread threadMoveM1  = Thread();
Thread threadMoveM2  = Thread();
Thread threadMoveM3  = Thread();
Thread threadMoveM4  = Thread();
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
void processInput(String msg);
void move_to_absolute(MotorAxis axis, float target_angle, float max_nb_steps);
Motor* get_motor(MotorAxis axis);


void receiveTask();

void moveM1Task();
void moveM2Task();
void moveM3Task();
void moveM4Task();

void sendTask();


void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }  // Wait for Serial ready





  // initialize motor table (match pins and initial 8 degrees)
  motors[DETECTOR_AZ]  = {"DET_AZ",  DET_AZ_STEP,  DET_AZ_DIR, DET_AZ_STEPS_PER_DEG,  long(8 * DET_AZ_STEPS_PER_DEG)};
  motors[DETECTOR_RAD] = {"DET_RAD", DET_RAD_STEP, DET_RAD_DIR, DET_RAD_STEPS_PER_DEG, long(8 * DET_RAD_STEPS_PER_DEG)};
  motors[LIGHT_AZ]     = {"LIGHT_AZ",LIGHT_AZ_STEP, LIGHT_AZ_DIR, LIGHT_AZ_STEPS_PER_DEG, long(8 * LIGHT_AZ_STEPS_PER_DEG)};
  motors[LIGHT_RAD]    = {"LIGHT_RAD",LIGHT_RAD_STEP, LIGHT_RAD_DIR, LIGHT_RAD_STEPS_PER_DEG, long(8 * LIGHT_RAD_STEPS_PER_DEG)};


  // Setup pins and encoders
  for (int i = 0; i < NUM_MOTORS; ++i) {
    pinMode(motors[i].step_pin, OUTPUT);
    pinMode(motors[i].dir_pin, OUTPUT);
  }

  Serial.println("Motor controller ready.");

  // --- Setup threads ---
  threadReceive.onRun(receiveTask);
  threadReceive.setInterval(RECEPTION_PERIOD);

  threadMoveM1.onRun(moveM1Task);
  threadMoveM1.setInterval(MOTION_PERIOD); 
  threadMoveM2.onRun(moveM2Task);
  threadMoveM2.setInterval(MOTION_PERIOD); 
  threadMoveM3.onRun(moveM3Task);
  threadMoveM3.setInterval(MOTION_PERIOD);
  threadMoveM4.onRun(moveM4Task);
  threadMoveM4.setInterval(MOTION_PERIOD);

  threadSend.onRun(sendTask);
  threadSend.setInterval(TRANSMISSION_PERIOD);



  // Add to controller
  controller.add(&threadReceive);
  controller.add(&threadMoveM1);
  controller.add(&threadMoveM2);
  controller.add(&threadMoveM3);
  controller.add(&threadMoveM4);
  controller.add(&threadSend);
}

void loop() {
  controller.run();  // this runs all active threads when ready
}


// === Auxiliary functions ===


Motor* get_motor(MotorAxis axis) {
    return &motors[(int)axis];
}

void move_to_absolute(MotorAxis axis, float target_angle, float max_nb_steps) {

    Motor* m = get_motor(axis);
  
    long target_steps = lround(target_angle * m->steps_per_deg);
    long step_diff = target_steps - m->current_steps;
    bool direction = (step_diff >= 0);
    long move_steps = min(abs(step_diff), max_nb_steps);

    // // 🔹 Print move_steps if positive
    // if (move_steps > 0) {
    //     Serial.print("Moving ");
    //     Serial.print(m->name);
    //     Serial.print(": ");
    //     Serial.print(move_steps);
    //     Serial.println(" steps");
    // }
    
    digitalWrite(m->dir_pin, direction ? HIGH : LOW);
    for (long i = 0; i < move_steps; i++) {
      digitalWrite(m->step_pin, HIGH);
      delayMicroseconds(STEP_DELAY_US);
      digitalWrite(m->step_pin, LOW);
      delayMicroseconds(STEP_DELAY_US);
    }
  
    long starting_pos = m->current_steps;
    m->current_steps = target_steps;
}


// --- Helper to parse 4 comma-separated floats ---
void processInput(String msg) {
  
    // Print the raw input message
    Serial.print("Arduino Received: ");
    Serial.println(msg);
    
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

void moveM1Task () {
    move_to_absolute(LIGHT_RAD, des_light_pol, LIGHT_RAD_STEPS_PER_DEG);
}
void moveM2Task () {
    move_to_absolute(DETECTOR_RAD, des_detector_pol, DET_RAD_STEPS_PER_DEG);
}
void moveM3Task () {
    move_to_absolute(DETECTOR_AZ, des_detector_azi, DET_AZ_STEPS_PER_DEG);
}
void moveM4Task () {
    move_to_absolute(LIGHT_AZ, des_light_azi, LIGHT_AZ_STEPS_PER_DEG);
}

// Send desired values back to Raspberry Pi
void sendTask() {
  Serial.print(des_light_azi, 1);
  Serial.print(',');
  Serial.print(des_light_pol, 1);
  Serial.print(',');
  Serial.print(des_detector_azi, 1);
  Serial.print(',');
  Serial.println(des_detector_pol, 1);
}
